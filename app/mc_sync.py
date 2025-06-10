from nicegui import ui
from mc_layout import Layout
from mc_directories import DirectorySelector
from mc_subprocess import list_syncs, add_sync, remove_sync


@ui.page("/sync")
def sync_page():
    layout = Layout()
    ui.page_title("Synchronization")

    with ui.column().classes("w-full") as tab_container:
        ui.label("Synchronization").classes("text-h5")
        Synchronization()
    layout.set_tab_container(tab_container)


class Synchronization:
    def __init__(self):
        self.local_paths = []
        self.table_container = None
        self._build_ui()

    def _build_ui(self):
        ui.label("List of local and cloud folders synchronized")
        self.table_container = ui.row().classes("w-full overflow-auto")
        self._refresh_ui()

        # Add dialog
        with ui.dialog() as add_dialog, ui.card():
            ui.label("Add Synchronization Pair").classes("text-lg font-bold")
            with ui.row().classes("w-full"):
                local_path_input = DirectorySelector("LOCALPATH", "/")
                remote_path_input = DirectorySelector("REMOTEPATH", "/", is_remote=True)

            def on_add():
                add_sync(
                    local_path_input.get_selected_path(),
                    remote_path_input.get_selected_path(),
                )
                add_dialog.close()
                self._refresh_ui()

            with ui.row():
                ui.button("Cancel", on_click=add_dialog.close)
                ui.button("OK", on_click=on_add)

        # Delete dialog
        with ui.dialog() as delete_dialog, ui.card():
            ui.label("Delete Synchronization Pair").classes("text-lg font-bold")
            selected_local = ui.select(self.local_paths, label="Select").classes(
                "w-full"
            )

            def on_delete():
                remove_sync(selected_local.value)
                delete_dialog.close()
                self._refresh_ui()

            with ui.row():
                ui.button("Cancel", on_click=delete_dialog.close)
                ui.button("OK", color="red", on_click=on_delete)

        with ui.row():

            def open_add_dialog():
                self._refresh_ui()
                add_dialog.open()

            def open_remove_dialog():
                self._refresh_ui()
                selected_local.clear()
                selected_local.set_options(self.local_paths)
                delete_dialog.open()

            ui.button(icon="add", on_click=open_add_dialog).classes("mt-6")
            ui.button(icon="delete", on_click=open_remove_dialog).classes("mt-6")
            ui.button(icon="refresh", on_click=self._refresh_ui).classes("mt-6")

    def _refresh_ui(self):
        self.table_container.clear()
        columns, rows, self.local_paths = list_syncs()
        with self.table_container:
            ui.table(columns=columns, rows=rows).classes("w-full")
