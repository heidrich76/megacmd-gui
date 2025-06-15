import argparse
import importlib
from nicegui import app, ui
from mc_layout import add_tabs_style, create_tab
from mc_login import create_login_dialog, check_login
from mc_home import home_page
from mc_sync import sync_page
from mc_webdav import webdav_page
from mc_backup import backup_page
from mc_mount import mount_page
from mc_terminal import terminal_page
from mc_settings import settings_page


@ui.page("/")
def index_page():
    dark = ui.dark_mode(app.storage.general.get("dark", None))
    dark.bind_value(app.storage.general, "dark")

    login_dialog = create_login_dialog()

    last_active_page = app.storage.general.get("active_page", "/home")
    if last_active_page == "/":
        last_active_page = "/home"

    def on_tab_change(tab_name):
        app.storage.general["active_page"] = tab_name

    add_tabs_style()
    with ui.tabs() as tabs:
        create_tab("/home", "Home", "home")
        create_tab("/sync", "Synchronization", "sync")
        create_tab("/webdav", "WebDAV", "cloud")
        create_tab("/backup", "Backup", "backup")
        create_tab("/mount", "Mount", "storage")
        create_tab("/terminal", "Terminal", "terminal")
        create_tab("/settings", "Settings", "settings")

    tabs.on("update:model-value", lambda e: on_tab_change(e.args))

    with ui.tab_panels(tabs, value=last_active_page).classes("w-full"):
        with ui.tab_panel("/home"):
            home_page()
            check_login(login_dialog)
        with ui.tab_panel("/sync"):
            sync_page()
            check_login(login_dialog)
        with ui.tab_panel("/webdav"):
            webdav_page()
            check_login(login_dialog)
        with ui.tab_panel("/backup"):
            backup_page()
            check_login(login_dialog)
        with ui.tab_panel("/mount"):
            mount_page()
            check_login(login_dialog)
        with ui.tab_panel("/terminal"):
            terminal_page()
        with ui.tab_panel("/settings"):
            settings_page(dark)
            check_login(login_dialog)


app.add_static_files("/static", "static")
importlib.import_module("mc_websocket")

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
