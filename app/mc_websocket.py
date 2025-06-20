import asyncio
import fcntl
import json
import os
import pty
import select
import shlex
import signal
import struct
import subprocess
import threading
import termios
from fastapi import WebSocket
from nicegui import app


@app.websocket("/terminal")
async def terminal_socket(websocket: WebSocket):
    await websocket.accept()

    master_fd, slave_fd = pty.openpty()
    process = subprocess.Popen(
        shlex.split("tmux new-session -As default"),
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        preexec_fn=os.setsid,
    )
    loop = asyncio.get_event_loop()
    stop_event = threading.Event()

    def resize(cols: int, rows: int):
        # Structure: rows, cols, xpix, ypix
        size = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(master_fd, termios.TIOCSWINSZ, size)
        # Kill process for tmux resize
        os.kill(process.pid, signal.SIGWINCH)

    def read_loop():
        while not stop_event.is_set():
            rlist, _, _ = select.select([master_fd], [], [], 0.1)
            if master_fd in rlist:
                try:
                    data = os.read(master_fd, 1024)
                    if data:
                        if stop_event.is_set():
                            break
                        try:
                            loop.call_soon_threadsafe(
                                asyncio.create_task, websocket.send_bytes(data)
                            )
                        except RuntimeError:
                            stop_event.set()
                            break
                except OSError:
                    stop_event.set()
                    break

    threading.Thread(target=read_loop, daemon=True).start()

    try:
        while True:
            message = await websocket.receive_text()
            try:
                obj = json.loads(message)
                if obj.get("type") == "resize":
                    resize(obj.get("cols", 80), obj.get("rows", 24))
                    continue
            except json.JSONDecodeError:
                pass

            os.write(master_fd, message.encode())
    except:
        stop_event.set()
        process.terminate()
        try:
            process.wait(timeout=1)
        except:
            process.kill()
        os.close(master_fd)
