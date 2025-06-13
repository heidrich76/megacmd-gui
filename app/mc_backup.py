from nicegui import ui
from mc_layout import Layout, create_warning_label
from mc_directories import DirectorySelector
from mc_subprocess import (
    list_backups,
    add_backup,
    remove_backup,
)


@ui.page("/backup")
def backup_page():
    layout = Layout()
    ui.page_title("Backup")

    with ui.column().classes("w-full"):
        ui.label("Backup").classes("text-h5")
        BackupManager()
    layout.check_login()


class BackupManager:
    def __init__(self):
        self._local_paths = []
        self._table_container = None
        self._build_ui()

    def _build_ui(self):
        with ui.row().classes("items-center"):
            ui.label("Configured backups")
            create_warning_label("Experimental")
        self._table_container = ui.row().classes("w-full overflow-auto")
        self._refresh_ui()

        # Add dialog
        with ui.dialog() as add_dialog, ui.card():
            ui.label("Add new Backup").classes("text-lg font-bold")
            with ui.row().classes("w-full"):
                local_input = DirectorySelector("LOCAL", "/")
                remote_input = DirectorySelector("REMOTE", "/", is_remote=True)
            with ui.row():
                period_input = ui.input("Period", placeholder='e.g., "1d" or cron')
                num_input = ui.number(
                    label='Backups to store"', value=3, min=1, step=1, precision=0
                )

            def on_add():
                add_backup(
                    local_input.get_selected_path(),
                    remote_input.get_selected_path(),
                    period_input.value,
                    int(num_input.value),
                )
                add_dialog.close()
                self._refresh_ui()

            with ui.row():
                ui.button("Cancel", on_click=add_dialog.close)
                ui.button("OK", on_click=on_add)

        # Delete dialog
        with ui.dialog() as delete_dialog, ui.card():
            ui.label("Delete Backup").classes("text-lg font-bold")
            select = ui.select(self._local_paths, label="Select").classes("w-full")

            def on_del():
                remove_backup(select.value)
                delete_dialog.close()
                self._refresh_ui()

            with ui.row():
                ui.button("Cancel", on_click=delete_dialog.close)
                ui.button("OK", color="red", on_click=on_del)

        with ui.row():
            ui.button(
                icon="add", on_click=lambda: (self._refresh_ui(), add_dialog.open())
            ).classes("mt-6")
            ui.button(
                icon="delete",
                on_click=lambda: (
                    self._refresh_ui(),
                    select.set_options(self._local_paths),
                    delete_dialog.open(),
                ),
            ).classes("mt-6")
            ui.button(icon="refresh", on_click=self._refresh_ui).classes("mt-6")

    def _refresh_ui(self):
        self._table_container.clear()
        columns, rows, self._local_paths = list_backups()
        with self._table_container:
            ui.table(columns=columns, rows=rows).classes("w-full")
