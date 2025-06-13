from nicegui import app, context, ui
import asyncio
from mc_subprocess import whoami, login


def create_warning_label(text):
    ui.label(text).classes(
        "text-sm bg-orange-200 text-orange-900 font-semibold px-3 py-1 rounded ml-2"
    )


def get_active_page():
    return "/" + context.client.request.url.path.split("/")[-1]


class Layout:
    def __init__(self):
        self._user_label = None
        self._login_dialog = None
        self.dark = None
        self._build_ui()

    def _build_ui(self):
        active_page = get_active_page()
        app.storage.general["active_page"] = active_page
        self.dark = ui.dark_mode(app.storage.general.get("dark", None))
        self.dark.bind_value(app.storage.general, "dark")

        def menu_button(text, link, icon="link"):
            active = active_page == link
            button = (
                ui.button(text, on_click=lambda: ui.navigate.to(link), icon=icon)
                .classes("w-full")
                .props("no-caps align=left")
            )
            if active:
                button.props("flat text-color=blue-5").classes(
                    "bg-blue-400 bg-opacity-20"
                )
            else:
                button.props("flat text-color=grey-7")

        with ui.left_drawer(fixed=False).props("bordered") as drawer:
            with ui.column().classes("h-full w-full justify-between"):
                with ui.column().classes("w-full"):
                    menu_button("Home", "/home", "home")
                    menu_button("Synchronization", "/sync", "sync")
                    menu_button("WebDAV", "/webdav", "cloud")
                    menu_button("Backup", "/backup", "backup")
                    menu_button("Mounting", "/mount", "storage")
                    menu_button("Terminal", "/terminal", "terminal")
                menu_button("Settings", "/settings", "settings")

        with ui.header(elevated=True).classes("items-center justify-between"):
            ui.button(on_click=lambda: drawer.toggle(), icon="menu").props(
                "flat color=white"
            )
            self._user_label = ui.label("").props("dense")

        with ui.dialog() as self._login_dialog, ui.card().classes("w-full"):
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
                self._refresh_ui()
                login_button.enable()
                await_dialog.close()
                self._login_dialog.close()
                ui.navigate.to("/home")

            with ui.row():
                ui.button("Cancel", on_click=self._login_dialog.close)
                login_button = ui.button("OK", on_click=login_click).props(
                    "color=positive"
                )

            with ui.dialog().props("persistent") as await_dialog:
                with ui.card():
                    with ui.column().classes("items-center"):
                        ui.spinner(size="lg", color="primary")
                        ui.label("Please wait (may take a while)...").classes("mt-4")
        self._refresh_ui()

    def _refresh_ui(self):
        self._user_label.text = whoami()

    def check_login(self):
        if self._user_label.text == "":
            ui.button("Login", on_click=self._login_dialog.open)
            return True
        return False
