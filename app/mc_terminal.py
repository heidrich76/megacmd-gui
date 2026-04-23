# Code adapted based on NiceGUI example: https://github.com/zauberzeug/nicegui/blob/main/examples/xterm/main.py
import asyncio
import fcntl
import os
import pty
import signal
import struct
import termios
from nicegui import core, events, ui
from mc_layout import create_warning_label


def terminal_page():
    ui.page_title("Terminal")
    create_warning_label("Be careful, you have full access to the container")

    client = ui.context.client
    pty_state = {"pid": -1, "fd": -1}

    with ui.column().classes("w-full"):
        terminal = ui.xterm().classes("w-full min-h-[400px] h-[calc(100dvh-200px)]")
        ui.element("q-resize-observer").on("resize", terminal.fit)

    @terminal.on_data
    def terminal_to_pty(event: events.XtermDataEventArguments):
        fd = pty_state["fd"]
        if fd < 0:
            return
        try:
            os.write(fd, event.data.encode("utf-8"))
        except OSError:
            pass

    @terminal.on_resize
    def resize_terminal(event: events.XtermResizeEventArguments):
        fd = pty_state["fd"]
        if fd < 0:
            return
        try:
            fcntl.ioctl(
                fd,
                termios.TIOCSWINSZ,
                struct.pack("HHHH", event.rows, event.cols, 0, 0),
            )
        except OSError:
            pass

    async def start_terminal():
        await client.connected()

        pid, fd = pty.fork()
        if pid == 0:
            os.environ["TERM"] = "xterm-256color"
            os.environ["COLORTERM"] = "truecolor"
            os.execvp("/bin/bash", ["/bin/bash"])

        pty_state["pid"] = pid
        pty_state["fd"] = fd

        def pty_to_terminal():
            try:
                data = os.read(fd, 1024)
            except OSError:
                data = b""

            if not data:
                try:
                    core.loop.remove_reader(fd)
                except Exception:
                    pass
                return

            if not terminal.is_deleted:
                terminal.write(data.decode(errors="ignore"))

        core.loop.add_reader(fd, pty_to_terminal)
        terminal.fit()

    async def cleanup():
        fd = pty_state["fd"]
        pid = pty_state["pid"]

        if fd >= 0:
            try:
                core.loop.remove_reader(fd)
            except Exception:
                pass
            try:
                os.close(fd)
            except OSError:
                pass
            pty_state["fd"] = -1

        if pid > 0:
            try:
                os.kill(pid, signal.SIGHUP)
            except OSError:
                pass
            try:
                os.waitpid(pid, 0)
            except (ChildProcessError, OSError):
                pass
            pty_state["pid"] = -1

    asyncio.create_task(start_terminal())
    client.on_disconnect(cleanup)
