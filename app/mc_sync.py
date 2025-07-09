from nicegui import ui
import time
from mc_directories import DirectorySelector
from mc_layout import create_action_table, create_ok_cancel_row, create_add_refresh_row
from mc_subprocess import (
    list_syncs,
    add_sync,
    remove_sync,
    list_sync_issues,
    list_sync_issue_details,
    remove_sync_issue,
)


@ui.refreshable
def create_sync_table():
    # Delete dialog
    def show_delete_dialog(row):
        with ui.dialog() as dialog, ui.card():
            ui.label("Delete Synchronization Pair").classes("text-lg font-bold")
            ui.label(f"Local Path: {row["LOCALPATH"]}")
            ui.label(f"Remote Path: {row["REMOTEPATH"]}")

            def on_delete():
                remove_sync(row["LOCALPATH"])
                dialog.close()
                create_sync_table.refresh()

            create_ok_cancel_row(cancel_cb=dialog.close, ok_cb=on_delete)
        dialog.open()

    # Show synchronization table
    columns, rows = list_syncs()
    with ui.row().classes("w-full overflow-auto"):
        create_action_table(
            columns=columns, rows=rows, action_cb=show_delete_dialog, icon="delete"
        ).classes("w-full")

    # Add dialog
    def show_add_dialog():
        with ui.dialog() as dialog, ui.card():
            ui.label("Add Synchronization Pair").classes("text-lg font-bold")
            with ui.row().classes("w-full"):
                local_path_input = DirectorySelector("LOCALPATH", "/")
                remote_path_input = DirectorySelector("REMOTEPATH", "/", is_remote=True)

            def on_add():
                add_sync(
                    local_path_input.get_selected_path(),
                    remote_path_input.get_selected_path(),
                )
                dialog.close()
                create_sync_table.refresh()

            create_ok_cancel_row(cancel_cb=dialog.close, ok_cb=on_add)
        dialog.open()

    create_add_refresh_row(add_cb=show_add_dialog, refreshable=create_sync_table)

    # Show issues table with details button
    ui.label("Issues").classes("text-h6")

    def show_issue_dialog(row):
        with ui.dialog() as dialog, ui.card().classes("w-full").style(
            "max-width: 90vw;"
        ):
            ui.label("Issue").classes("text-lg font-bold")
            description, columns, rows = list_sync_issue_details(row["ISSUE_ID"])
            ui.label(description).style("white-space: pre-wrap")

            # Delete issue dialog
            def show_delete_issue_dialog(row):
                with ui.dialog() as dialog, ui.card():
                    ui.label("Delete Issue Path").classes("text-lg font-bold")
                    ui.label(f"Path: {row["PATH"]}")

                    def on_delete():
                        remove_sync_issue(row["PATH"])
                        dialog.close()
                        # Wait for megacmd to analyze new situation
                        time.sleep(1)
                        create_sync_table.refresh()

                    create_ok_cancel_row(cancel_cb=dialog.close, ok_cb=on_delete)
                dialog.open()

            create_action_table(
                columns=columns,
                rows=rows,
                action_cb=show_delete_issue_dialog,
                icon="delete",
            ).classes("w-full")

            ui.button("Close", on_click=dialog.close)
        dialog.open()

    with ui.row().classes("w-full overflow-auto"):
        columns, rows = list_sync_issues()
        create_action_table(
            columns=columns, rows=rows, action_cb=show_issue_dialog
        ).classes("w-full")


def sync_page():
    ui.page_title("Synchronization")

    with ui.column().classes("w-full"):
        ui.label("Synchronization").classes("text-h5")
        ui.label("List of local and cloud folders synchronized")
        create_sync_table()
