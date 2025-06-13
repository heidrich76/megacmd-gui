from nicegui import app, ui
from mc_layout import Layout
from mc_subprocess import whoami, version, logout


@ui.page("/settings")
def settings_page():
    layout = Layout()
    ui.page_title("Settings")

    with ui.dialog() as logout_dialog, ui.card():
        ui.label("Do you really want to log out?")

        def on_logout():
            logout()
            logout_dialog.close()
            ui.navigate.to("/")

        with ui.row():
            ui.button("Cancel", on_click=logout_dialog.close)
            ui.button("Yes", on_click=on_logout).props("color=negative")

    with ui.column().classes("w-full"):
        ui.label("Settings").classes("text-h5")

        with ui.grid(columns="auto auto"):
            ui.label("User:")
            ui.label(whoami())
            ui.label("Version:")
            ui.label(version())

            ui.label("Mode:")
            options = {"Auto": None, "Light": False, "Dark": True}
            reversed_options = {None: "Auto", False: "Light", True: "Dark"}
            dark_select = ui.select(
                options=list(options.keys()),
                on_change=lambda e: setattr(layout.dark, "value", options[e.value]),
            ).props("dense")
            dark_select.value = reversed_options[layout.dark.value]

    if not layout.check_login():
        ui.button("Logout", on_click=logout_dialog.open)
