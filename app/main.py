from nicegui import app, ui
import argparse
import importlib

importlib.import_module("mc_sync")
importlib.import_module("mc_webdav")
importlib.import_module("mc_backup")
importlib.import_module("mc_mount")
importlib.import_module("mc_terminal")


@ui.page("/")
def index_page():
    ui.navigate.to("/sync")


app.add_static_files("/static", "static")

parser = argparse.ArgumentParser(description="Start the MEGAcmd NiceGUI app.")
parser.add_argument("--host", default="0.0.0.0", help="Host address to bind to")
parser.add_argument("--port", type=int, default=8080, help="Port number to bind to")
parser.add_argument(
    "--reload", type=bool, default=False, help="Enable autoreload (development mode)"
)
parser.add_argument(
    "--show", type=bool, default=False, help="Show browser window on start"
)
parser.add_argument(
    "--log-level",
    default="error",
    choices=["critical", "error", "warning", "info", "debug", "trace"],
    help="Uvicorn logging level",
)

args = parser.parse_args()

try:
    ui.run(
        host=args.host,
        port=args.port,
        reload=args.reload,
        show=args.show,
        uvicorn_logging_level=args.log_level,
    )
except KeyboardInterrupt:
    print("NiceGUI server stopped via keyboard interrupt")
