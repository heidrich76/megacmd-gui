from nicegui import ui
from mc_layout import (
    create_warning_label,
    create_action_table,
    create_ok_cancel_row,
    create_add_refresh_row,
)
from mc_directories import DirectorySelector
from mc_subprocess import (
    list_backups,
    add_backup,
    remove_backup,
)


@ui.refreshable
def create_backup_table():
    # Delete dialog
    def show_delete_dialog(row):
        with ui.dialog() as dialog, ui.card():
            ui.label("Delete Backup").classes("text-lg font-bold")
            ui.label(f"Path: {row["LOCALPATH"]}")

            def on_delete():
                remove_backup(row["LOCALPATH"])
                dialog.close()
                create_backup_table.refresh()

            create_ok_cancel_row(cancel_cb=dialog.close, ok_cb=on_delete)
        dialog.open()

    # Show backup table
    columns, rows = list_backups()
    with ui.row().classes("w-full overflow-auto"):
        create_action_table(
            columns=columns, rows=rows, action_cb=show_delete_dialog, icon="delete"
        ).classes("w-full")

    # Add dialog
    def show_add_dialog():
        with ui.dialog() as dialog, ui.card():
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
                dialog.close()
                create_backup_table.refresh()

            create_ok_cancel_row(cancel_cb=dialog.close, ok_cb=on_add)
        dialog.open()

    create_add_refresh_row(
        add_cb=show_add_dialog, refresh_cb=create_backup_table.refresh
    )


def backup_page():
    ui.page_title("Backup")

    with ui.column().classes("w-full"):
        ui.label("Backup").classes("text-h5")
        with ui.row().classes("items-center"):
            ui.label("Configured backups")
            create_warning_label("Experimental")
        create_backup_table()
