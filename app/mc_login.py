import asyncio
from nicegui import app, ui
from mc_subprocess import login, is_logged_in


def create_login_dialog():
    with ui.dialog() as login_dialog, ui.card().classes("w-full"):
        ui.label("MEGA Login").classes("text-lg font-bold")
        email = ui.input("E-Mail")
        email.props("type=email").style("width: 100%")
        email.bind_value(app.storage.general, "email")
        password = ui.input("Password", password=True).style("width: 100%")

        async def login_click():
            login_button.disable()
            await_dialog.open()
            await login(email.value, password.value)
            # Sleep for letting megacmd settle
            await asyncio.sleep(1)
            login_button.enable()
            await_dialog.close()
            login_dialog.close()
            ui.navigate.reload()

        with ui.row():
            ui.button("Cancel", on_click=login_dialog.close)
            login_button = ui.button("OK", on_click=login_click).props("color=positive")

        with ui.dialog().props("persistent") as await_dialog:
            with ui.card():
                with ui.column().classes("items-center"):
                    ui.spinner(size="lg", color="primary")
                    ui.label("Please wait (may take a while)...").classes("mt-4")
    return login_dialog


def check_login(login_dialog):
    if not is_logged_in():
        ui.button("Login", on_click=login_dialog.open)
        return True
    return False
