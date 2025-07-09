from nicegui import ui
from mc_layout import (
    create_warning_label,
    create_action_table,
    create_ok_cancel_row,
    create_add_refresh_row,
)
from mc_directories import DirectorySelector
from mc_subprocess import list_mounts, add_mount, remove_mount


@ui.refreshable
def create_mount_table():
    # Delete dialog
    def show_delete_dialog(row):
        with ui.dialog() as dialog, ui.card():
            ui.label("Delete Mount").classes("text-lg font-bold")
            ui.label(f"Path: {row["LOCAL_PATH"]}")

            def on_delete():
                remove_mount(row["LOCAL_PATH"])
                dialog.close()
                create_mount_table.refresh()

            create_ok_cancel_row(cancel_cb=dialog.close, ok_cb=on_delete)
        dialog.open()

    # Show mount table
    columns, rows = list_mounts()
    with ui.row().classes("w-full overflow-auto"):
        create_action_table(
            columns=columns, rows=rows, action_cb=show_delete_dialog, icon="delete"
        ).classes("w-full")

    # Add dialog
    def show_add_dialog():
        with ui.dialog() as dialog, ui.card():
            ui.label("Add Mount").classes("text-lg font-bold")
            with ui.row().classes("w-full"):
                local_input = DirectorySelector("LOCAL", "/")
                remote_input = DirectorySelector("REMOTE", "/", is_remote=True)
            with ui.row():
                name_input = ui.input("Name")
                disabled = ui.checkbox("Disabled", value=False)
                transient = ui.checkbox("Transient", value=False)
                read_only = ui.checkbox("Read-only", value=False)

            def on_add():
                add_mount(
                    local_input.get_selected_path(),
                    remote_input.get_selected_path(),
                    name=name_input.value,
                    disabled=disabled.value,
                    transient=transient.value,
                    read_only=read_only.value,
                )
                dialog.close()
                create_mount_table.refresh()

            create_ok_cancel_row(cancel_cb=dialog.close, ok_cb=on_add)
        dialog.open()

    create_add_refresh_row(add_cb=show_add_dialog, refreshable=create_mount_table)


def mount_page():
    ui.page_title("Mounting")
    with ui.column().classes("w-full"):
        ui.label("Mounting").classes("text-h5")
        with ui.row().classes("items-center"):
            ui.label("List of configured mounts")
            create_warning_label("Experimental")
        create_mount_table()
