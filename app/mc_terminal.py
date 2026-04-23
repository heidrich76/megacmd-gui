# Code adapted based on NiceGUI example: https://github.com/zauberzeug/nicegui/blob/main/examples/xterm/main.py
import asyncio
import contextlib
import fcntl
import os
import pty
import signal
import struct
import termios
from nicegui import app, core, events, ui
from mc_layout import create_warning_label


def terminal_page():
    ui.page_title("Terminal")
    create_warning_label("Be careful, you have full access to the container")

    client = ui.context.client

    state = {
        "pid": -1,
        "fd": -1,
        "closed": False,
        "reader_installed": False,
        "start_task": None,
    }

    with ui.column().classes("w-full"):
        terminal = ui.xterm().classes("w-full min-h-[400px] h-[calc(100dvh-200px)]")
        resize_observer = ui.element("q-resize-observer")

    def is_alive() -> bool:
        return not state["closed"] and not terminal.is_deleted

    def safe_fit() -> None:
        if not is_alive():
            return
        with contextlib.suppress(Exception):
            terminal.fit()

    def remove_reader() -> None:
        fd = state["fd"]
        if fd >= 0 and state["reader_installed"]:
            with contextlib.suppress(Exception):
                core.loop.remove_reader(fd)
            state["reader_installed"] = False

    def close_fd() -> None:
        fd = state["fd"]
        if fd >= 0:
            with contextlib.suppress(OSError):
                os.close(fd)
            state["fd"] = -1

    def terminate_child() -> None:
        pid = state["pid"]
        if pid > 0:
            with contextlib.suppress(OSError):
                os.kill(pid, signal.SIGHUP)
            with contextlib.suppress(ChildProcessError, OSError):
                os.waitpid(pid, 0)
            state["pid"] = -1

    @terminal.on_data
    def terminal_to_pty(event: events.XtermDataEventArguments) -> None:
        fd = state["fd"]
        if state["closed"] or fd < 0:
            return
        with contextlib.suppress(OSError):
            os.write(fd, event.data.encode("utf-8"))

    @terminal.on_resize
    def resize_terminal(event: events.XtermResizeEventArguments) -> None:
        fd = state["fd"]
        if state["closed"] or fd < 0:
            return
        with contextlib.suppress(OSError):
            fcntl.ioctl(
                fd,
                termios.TIOCSWINSZ,
                struct.pack("HHHH", event.rows, event.cols, 0, 0),
            )

    resize_observer.on("resize", lambda: safe_fit())

    def pty_to_terminal() -> None:
        fd = state["fd"]

        if state["closed"] or fd < 0 or terminal.is_deleted:
            remove_reader()
            return

        try:
            data = os.read(fd, 1024)
        except OSError:
            data = b""

        if not data:
            remove_reader()
            return

        if not is_alive():
            remove_reader()
            return

        with contextlib.suppress(Exception):
            terminal.write(data.decode(errors="ignore"))

    async def start_terminal() -> None:
        await client.connected()

        if state["closed"] or terminal.is_deleted:
            return

        pid, fd = pty.fork()
        if pid == 0:
            os.environ["TERM"] = "xterm-256color"
            os.environ["COLORTERM"] = "truecolor"
            os.execvp("/bin/bash", ["/bin/bash"])

        state["pid"] = pid
        state["fd"] = fd

        core.loop.add_reader(fd, pty_to_terminal)
        state["reader_installed"] = True

        safe_fit()

    async def cleanup() -> None:
        if state["closed"]:
            return

        state["closed"] = True

        task = state["start_task"]
        if task is not None and task is not asyncio.current_task():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await task
            state["start_task"] = None

        remove_reader()
        close_fd()
        terminate_child()

    state["start_task"] = asyncio.create_task(start_terminal())

    client.on_disconnect(cleanup)

    app.on_shutdown(lambda: asyncio.create_task(cleanup()))
