from nicegui import app, ui
import argparse
import importlib
from mc_layout import Layout, create_warning_label

importlib.import_module("mc_sync")
importlib.import_module("mc_webdav")
importlib.import_module("mc_backup")
importlib.import_module("mc_mount")
importlib.import_module("mc_terminal")
importlib.import_module("mc_settings")


@ui.page("/")
def index_page():
    layout = Layout()
    ui.page_title("Home")

    ui.label("Home").classes("text-h5")
    ui.add_css(
        """
.nicegui-markdown a, .nicegui-markdown a:visited {
    color: grey;
    text-decoration: none;
}
.nicegui-markdown a:hover {
    color: grey;
    text-decoration: underline;
}
"""
    )
    ui.markdown(
        """
This app provides a simple web-based user interface for [MEGAcmd](https://github.com/meganz/MEGAcmd).
It allows using MEGAcmd for synchronizing your files with the [MEGA cloud](https://mega.nz/).

**Features**

- **Logging In:** Authenticate and gain access to your MEGA account within the web interface.
- **File and Folder Synchronization:** Manage active synchronization tasks between local directories and your MEGA cloud storage.
- **WebDAV Access:** Potentially expose your MEGA cloud storage via WebDAV for integration with other applications or file managers.
- **Backup Management:** Dedicated functionality for creating and managing backups to your MEGA cloud storage.
- **Cloud Drive Mounting:** Mount your MEGA cloud storage as a local filesystem for seamless access through your operating system's file explorer.
- **Integrated Terminal Access:** Provides direct command-line access to MegaCMD for advanced operations and scripting within the web interface.
- [Complete MEGAcmd user guide](https://github.com/meganz/MEGAcmd/blob/master/UserGuide.md)
"""
    )
    create_warning_label("This add-on is provided as-is. Use at your own risk.")
    layout.check_login()


app.add_static_files("/static", "static")

if __name__ in {"__main__", "__mp_main__"}:
    parser = argparse.ArgumentParser(description="Start the MEGAcmd NiceGUI app.")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port number to bind to")
    parser.add_argument(
        "--reload",
        type=bool,
        default=False,
        help="Enable autoreload (development mode)",
    )
    parser.add_argument(
        "--show", type=bool, default=False, help="Show browser window on start"
    )
    parser.add_argument(
        "--log_level",
        default="error",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Uvicorn logging level",
    )
    parser.add_argument("--root_path", default="", help="Root path to use")

    args = parser.parse_args()
    app.storage.general["root_path"] = args.root_path

    try:
        ui.run(
            host=args.host,
            port=args.port,
            reload=args.reload,
            show=args.show,
            uvicorn_logging_level=args.log_level,
            root_path=args.root_path,
        )
    except KeyboardInterrupt:
        print("NiceGUI server stopped via keyboard interrupt")
