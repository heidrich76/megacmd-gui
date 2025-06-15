from nicegui import ui
from mc_layout import create_warning_label
from mc_directories import DirectorySelector
from mc_subprocess import (
    list_backups,
    add_backup,
    remove_backup,
)


@ui.refreshable
def create_backup_table():
    columns, rows, local_paths = list_backups()
    with ui.row().classes("w-full overflow-auto"):
        ui.table(columns=columns, rows=rows).classes("w-full")

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
            create_backup_table.refresh()

        with ui.row():
            ui.button("Cancel", on_click=add_dialog.close)
            ui.button("OK", on_click=on_add)

    # Delete dialog
    with ui.dialog() as delete_dialog, ui.card():
        ui.label("Delete Backup").classes("text-lg font-bold")
        path_select = ui.select(local_paths, label="Select").classes("w-full")

        def on_del():
            remove_backup(path_select.value)
            delete_dialog.close()
            create_backup_table.refresh()

        with ui.row():
            ui.button("Cancel", on_click=delete_dialog.close)
            ui.button("OK", color="red", on_click=on_del)

    with ui.row():
        ui.button(icon="add", on_click=add_dialog.open).classes("mt-6")
        ui.button(icon="delete", on_click=delete_dialog.open).classes("mt-6")
        ui.button(icon="refresh", on_click=create_backup_table.refresh).classes("mt-6")


def backup_page():
    ui.page_title("Backup")

    with ui.column().classes("w-full"):
        ui.label("Backup").classes("text-h5")
        with ui.row().classes("items-center"):
            ui.label("Configured backups")
            create_warning_label("Experimental")
        create_backup_table()
