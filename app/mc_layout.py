from nicegui import app, context, ui
import asyncio
from mc_subprocess import version, whoami, login, logout


def create_warning_label(text):
    ui.label(text).classes(
        "text-sm bg-orange-200 text-orange-900 font-semibold px-3 py-1 rounded ml-2"
    )


class Layout:
    def __init__(self):
        self.user_label = None
        self.logout_button = None
        self.version_label = None
        self.login_card = None
        self.tab_container = None
        self._build_ui()

    def _build_ui(self):
        current_path = context.client.request.url.path

        def menu_button(text, link):
            active = current_path.startswith(link)
            return (
                ui.button(text, on_click=lambda: ui.navigate.to(link))
                .props("flat")
                .props("color=primary" if active else "color=default")
            )

        with ui.left_drawer(fixed=False).props("bordered") as drawer:

            menu_button("Home", "/")
            menu_button("Synchronization", "/sync")
            menu_button("WebDAV", "/webdav")
            menu_button("Backup", "/backup")
            menu_button("Mounting", "/mount")
            menu_button("Terminal", "/terminal")

            def on_logout():
                logout()
                self._refresh_ui()

            self.logout_button = ui.button("Logout", on_click=on_logout)

        with ui.header(elevated=True).style("background-color: #3874c8").classes(
            "items-center justify-between"
        ):
            ui.button(on_click=lambda: drawer.toggle(), icon="menu").props(
                "flat color=white"
            )
            self.user_label = ui.label("").props("dense")

        with ui.footer(elevated=True).style("background-color: #3874c8").classes(
            "items-center justify-between"
        ):
            self.version_label = ui.label("").props("dense")

            if app.storage.general.get("dark", "NA") == "NA":
                app.storage.general["dark"] = None

            dark = ui.dark_mode()
            dark.bind_value(app.storage.general, "dark")
            options = {"Auto": None, "Light": False, "Dark": True}
            reversed_options = {None: "Auto", False: "Light", True: "Dark"}
            dark_select = ui.select(
                options=list(options.keys()),
                on_change=lambda e: setattr(dark, "value", options[e.value]),
            ).props("dense")
            dark_select.value = reversed_options[dark.value]

        with ui.row().classes("w-full justify-center") as self.login_card:
            with ui.card().classes("w-96"):
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

                login_button = ui.button("Login", on_click=login_click)

                with ui.dialog().props("persistent") as await_dialog:
                    with ui.card():
                        with ui.column().classes("items-center"):
                            ui.spinner(size="lg", color="primary")
                            ui.label("Please wait (may take a while)...").classes(
                                "mt-4"
                            )

    def _refresh_ui(self):
        self.version_label.text = version()
        self.user_label.text = whoami()

        if self.user_label.text == "":
            self.logout_button.disable()
            self.login_card.visible = True
        else:
            self.logout_button.enable()
            self.login_card.visible = False

        if self.tab_container is not None:
            self.tab_container.visible = not self.login_card.visible

    def set_tab_container(self, container):
        self.tab_container = container
        self._refresh_ui()
