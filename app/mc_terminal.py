from nicegui import ui, app
from fastapi import WebSocket
from pathlib import Path
import asyncio
import os
import pty
import select
import threading
import fcntl
import termios
import struct
import json
from mc_layout import Layout, create_warning_label

js_path = Path(__file__).parent / "static" / "terminal.js"
js_code = js_path.read_text(encoding="utf8")


@ui.page("/terminal")
def terminal_page():
    layout = Layout()
    ui.page_title("Terminal")
    ui.label("Terminal").classes("text-h5")

    with ui.row().classes("items-center"):
        ui.label(
            "Terminal is for expert users and gives full access to the MEGAcmd container"
        )
        create_warning_label("Be carefull!")

    root_path = app.storage.general.get("root_path", "")
    rp_js_code = js_code.replace("/terminal", f"{root_path}/terminal")
    ui.add_head_html(
        f"""
        <script src="{root_path}/static/xterm.js"></script>
        <link rel="stylesheet" href="{root_path}/static/xterm.css" />
        <script src="{root_path}/static/addon-fit.js"></script>
        <script>{rp_js_code}</script>
        """
    )

    with ui.column().props("id=terminal").classes(
        "w-full min-h-[400px] h-[calc(100vh-320px)] shadow-lg"
    ):
        pass

    layout._refresh_ui()


@app.websocket("/terminal")
async def terminal_socket(websocket: WebSocket):
    await websocket.accept()
    master_fd, slave_fd = pty.openpty()

    pid = os.fork()
    if pid == 0:
        os.setsid()
        os.dup2(slave_fd, 0)
        os.dup2(slave_fd, 1)
        os.dup2(slave_fd, 2)
        os.execlp("bash", "bash")
    else:
        loop = asyncio.get_event_loop()
        stop_event = threading.Event()

        def resize(cols: int, rows: int):
            # Structure: rows, cols, xpix, ypix
            size = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(master_fd, termios.TIOCSWINSZ, size)

        def read_loop():
            while not stop_event.is_set():
                rlist, _, _ = select.select([master_fd], [], [], 0.1)
                if master_fd in rlist:
                    try:
                        data = os.read(master_fd, 1024)
                        # Create thread-safe task - not disturbing event loop
                        loop.call_soon_threadsafe(
                            asyncio.create_task, websocket.send_bytes(data)
                        )
                    except OSError:
                        break

        threading.Thread(target=read_loop, daemon=True).start()

        try:
            while True:
                message = await websocket.receive_text()
                try:
                    obj = json.loads(message)
                    if obj.get("type") == "resize":
                        cols = obj.get("cols", 80)
                        rows = obj.get("rows", 24)
                        resize(cols, rows)
                        continue
                except json.JSONDecodeError:
                    pass

                os.write(master_fd, message.encode())
        except:
            # Avoid zombie processes
            stop_event.set()
            try:
                os.kill(pid, 9)
                os.waitpid(pid, 0)
            except ProcessLookupError:
                pass
            try:
                os.close(master_fd)
            except OSError:
                pass
