from nicegui import app, ui
from mc_layout import Layout
from mc_directories import DirectorySelector
from mc_subprocess import list_webdavs, add_webdav, remove_webdav


@ui.page("/webdav")
def webdav_page():
    layout = Layout()
    ui.page_title("WebDAV")

    with ui.column().classes("w-full") as tab_container:
        ui.label("WebDAV").classes("text-h5")
        WebDAV()
    layout.set_tab_container(tab_container)


class WebDAV:
    def __init__(self):
        self.local_paths = []
        self.table_container = None
        self._build_ui()

    def _build_ui(self):
        ui.label("Currently served WebDAV folders")
        self.table_container = ui.row().classes("w-full overflow-auto")
        ui.input(label="Base URL", on_change=lambda: self._refresh_ui()).classes(
            "w-full"
        ).bind_value(app.storage.general, "webdav_base_url")

        self._refresh_ui()

        # Add dialog
        with ui.dialog() as serve_dialog, ui.card():
            ui.label("Serve WebDAV Path").classes("text-lg font-bold")
            remote_path_input = DirectorySelector("REMOTEPATH", "/", is_remote=True)
            ui.checkbox(text="Start with public option").bind_value(
                app.storage.general, "webdav_is_public"
            )

            with ui.row():
                ui.button("Cancel", on_click=serve_dialog.close)

                def on_serve():
                    remote_path = remote_path_input.get_selected_path()
                    is_public = app.storage.general.get("webdav_is_public", False)
                    add_webdav(remote_path, is_public)
                    self._refresh_ui()
                    serve_dialog.close()

                ui.button("OK", on_click=on_serve)

        # Delete dialog
        with ui.dialog() as unserve_dialog, ui.card():
            ui.label("Unserve WebDAV Path").classes("text-lg font-bold")
            path_select = ui.select([], label="Path").classes("w-full")
            with ui.row():
                ui.button("Cancel", on_click=unserve_dialog.close)

                def on_unserve():
                    remote_path = path_select.value
                    remove_webdav(remote_path)
                    self._refresh_ui()
                    unserve_dialog.close()

                ui.button("OK", color="red", on_click=on_unserve)

        def open_serve_dialog():
            self._refresh_ui()
            serve_dialog.open()

        def open_unserve_dialog():
            self._refresh_ui()
            path_select.clear()
            path_select.set_options(self.local_paths)
            unserve_dialog.open()

        with ui.row():
            ui.button(icon="add", on_click=open_serve_dialog).classes("mt-6")
            ui.button(icon="delete", on_click=open_unserve_dialog).classes("mt-6")
            ui.button(icon="refresh", on_click=self._refresh_ui).classes("mt-6")

    def _refresh_ui(self):
        self.table_container.clear()
        base_url = app.storage.general.get("webdav_base_url", "")
        columns, rows, self.local_paths = list_webdavs(base_url)

        with self.table_container:
            table = ui.table(columns=columns, rows=rows).classes("w-full")
            table.add_slot(
                "body-cell-URL",
                """
                    <q-td :props="props">
                        <a :href="props.value" target="_blank">{{ props.value }}</a>
                    </q-td>
                """,
            )
