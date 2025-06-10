from nicegui import ui
from mc_layout import Layout, create_warning_label
from mc_directories import DirectorySelector
from mc_subprocess import list_mounts, add_mount, remove_mount


@ui.page("/mount")
def mounts_page():
    layout = Layout()
    ui.page_title("Mounting")
    with ui.column().classes("w-full") as tab_container:
        ui.label("Mounting").classes("text-h5")
        MountManager()
    layout.set_tab_container(tab_container)


class MountManager:
    def __init__(self):
        self.local_paths = []
        self.table_container = None
        self._build_ui()

    def _build_ui(self):
        with ui.row().classes("items-center"):
            ui.label("List of configured mounts")
            create_warning_label("Experimental")

        self.table_container = ui.row().classes("w-full overflow-auto")
        self._refresh_ui()

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
                self._refresh_ui()

            with ui.row():
                ui.button("Cancel", on_click=add_dialog.close)
                ui.button("OK", on_click=on_add)

        # Delete dialog
        with ui.dialog() as remove_dialog, ui.card():
            ui.label("Delete Mount").classes("text-lg font-bold")
            select = ui.select(self.local_paths, label="Select").classes("w-full")

            def on_remove():
                remove_mount(select.value)
                remove_dialog.close()
                self._refresh_ui()

            with ui.row():
                ui.button("Cancel", on_click=remove_dialog.close)
                ui.button("OK", color="red", on_click=on_remove)

        # Action-Buttons
        with ui.row():
            ui.button(
                icon="add", on_click=lambda: (self._refresh_ui(), add_dialog.open())
            ).classes("mt-6")
            ui.button(
                icon="delete",
                on_click=lambda: (
                    self._refresh_ui(),
                    select.set_options(self.local_paths),
                    remove_dialog.open(),
                ),
            ).classes("mt-6")
            ui.button(icon="refresh", on_click=self._refresh_ui).classes("mt-6")

    def _refresh_ui(self):
        self.table_container.clear()
        columns, rows, self.local_paths = list_mounts()
        with self.table_container:
            ui.table(columns=columns, rows=rows).classes("w-full")
