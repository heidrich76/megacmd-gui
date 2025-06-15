from nicegui import ui
from mc_directories import DirectorySelector
from mc_subprocess import list_syncs, add_sync, remove_sync


@ui.refreshable
def create_sync_table():
    columns, rows, local_paths = list_syncs()
    with ui.row().classes("w-full overflow-auto"):
        ui.table(columns=columns, rows=rows).classes("w-full")

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
            create_sync_table.refresh()

        with ui.row():
            ui.button("Cancel", on_click=add_dialog.close)
            ui.button("OK", on_click=on_add)

    # Delete dialog
    with ui.dialog() as delete_dialog, ui.card():
        ui.label("Delete Synchronization Pair").classes("text-lg font-bold")
        selected_local = ui.select(local_paths, label="Select").classes("w-full")

        def on_delete():
            remove_sync(selected_local.value)
            delete_dialog.close()
            create_sync_table.refresh()

        with ui.row():
            ui.button("Cancel", on_click=delete_dialog.close)
            ui.button("OK", color="red", on_click=on_delete)

    with ui.row():
        ui.button(icon="add", on_click=add_dialog.open).classes("mt-6")
        ui.button(icon="delete", on_click=delete_dialog.open).classes("mt-6")
        ui.button(icon="refresh", on_click=create_sync_table.refresh).classes("mt-6")


def sync_page():
    ui.page_title("Synchronization")

    with ui.column().classes("w-full"):
        ui.label("Synchronization").classes("text-h5")
        ui.label("List of local and cloud folders synchronized")
        create_sync_table()
