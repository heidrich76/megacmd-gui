from nicegui import app, ui
from pathlib import Path
from mc_layout import create_warning_label


js_path = Path(__file__).parent / "static" / "terminal.js"
js_code = js_path.read_text(encoding="utf8")


def terminal_page():
    ui.page_title("Terminal")

    root_path = app.storage.general.get("root_path", "")
    rp_js_code = js_code.replace("/terminal", f"{root_path}/terminal")
    ui.add_css(
        """
        .xterm-viewport {
        overflow: hidden !important;
        }
         """
    )
    ui.add_head_html(
        f"""
        <script src="{root_path}/static/xterm.js"></script>
        <link rel="stylesheet" href="{root_path}/static/xterm.css" />
        <script src="{root_path}/static/addon-fit.js"></script>
        <script>{rp_js_code}</script>
        """
    )
    create_warning_label("Be careful, you have full access to the container")

    with ui.column().classes("w-full"):
        ui.column().props("id=terminal").classes(
            "w-full min-h-[400px] h-[calc(100dvh-200px)]"
        )
