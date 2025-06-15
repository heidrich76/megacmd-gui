from nicegui import ui
from mc_layout import create_warning_label
from mc_directories import DirectorySelector
from mc_subprocess import list_mounts, add_mount, remove_mount


@ui.refreshable
def create_mount_table():
    columns, rows, local_paths = list_mounts()
    with ui.row().classes("w-full overflow-auto"):
        ui.table(columns=columns, rows=rows).classes("w-full")

    # Add dialog
    with ui.dialog() as add_dialog, ui.card():
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
            add_dialog.close()
            create_mount_table.refresh()

        with ui.row():
            ui.button("Cancel", on_click=add_dialog.close)
            ui.button("OK", on_click=on_add)

    # Delete dialog
    with ui.dialog() as remove_dialog, ui.card():
        ui.label("Delete Mount").classes("text-lg font-bold")
        select = ui.select(local_paths, label="Select").classes("w-full")

        def on_remove():
            remove_mount(select.value)
            remove_dialog.close()
            create_mount_table.refresh()

        with ui.row():
            ui.button("Cancel", on_click=remove_dialog.close)
            ui.button("OK", color="red", on_click=on_remove)

    # Action-Buttons
    with ui.row():
        ui.button(icon="add", on_click=add_dialog.open).classes("mt-6")
        ui.button(icon="delete", on_click=remove_dialog.open).classes("mt-6")
        ui.button(icon="refresh", on_click=create_mount_table.refresh).classes("mt-6")


def mount_page():
    ui.page_title("Mounting")
    with ui.column().classes("w-full"):
        ui.label("Mounting").classes("text-h5")
        with ui.row().classes("items-center"):
            ui.label("List of configured mounts")
            create_warning_label("Experimental")
        create_mount_table()
