from nicegui import ui
import os
from mc_subprocess import ls, mkdir


class DirectorySelector:
    def __init__(self, title: str, start_path: str = "/", is_remote=False):
        self.title = title
        self.path_array = [start_path.rstrip("/")] if start_path != "/" else ["/"]
        self.path = self.get_selected_path()
        self.path_label = None
        self.select_box = None
        self.up_button = None
        self.is_remote = is_remote
        self._build_ui()

    def _build_ui(self):
        with ui.column().classes("p-4 border rounded shadow-md w-full"):
            ui.label(self.title).classes("text-lg font-bold")
            with ui.row():
                ui.label("Path:").classes("font-bold")
                self.path_label = ui.label("/")
            self.select_box = ui.select(options=[], label="Sub-folders").classes(
                "w-full"
            )

            def go_down():
                if self.select_box.value:
                    self.path_array.append(self.select_box.value)
                    self._refresh_ui()

            def go_up():
                if len(self.path_array) > 1:
                    self.path_array.pop()
                    self._refresh_ui()

            self.select_box.on("update:model-value", go_down)
            with ui.row():
                self.up_button = ui.button(icon="arrow_upward", on_click=go_up).props(
                    "dense flat"
                )
                with ui.row().classes("whitespace-nowrap items-right"):
                    new_folder = ui.input(placeholder="New folder").props(
                        "dense outlined"
                    )

                    def on_add():
                        new_dir = new_folder.value.strip()
                        if not new_dir:
                            ui.notify("Folder name cannot be empty", color="warning")
                            return
                        mkdir(self.path, new_dir, self.is_remote)
                        self._refresh_ui()

                    ui.button(icon="add", on_click=on_add).props("dense flat")
        self._refresh_ui()

    def _refresh_ui(self):
        self.path = self.get_selected_path()
        self.path_label.text = self.path

        subdirs = ls(self.path, self.is_remote)
        self.select_box.set_options(subdirs)
        if len(subdirs) == 0:
            self.select_box.disable()
        else:
            self.select_box.enable()
        self.select_box.value = None

        if len(self.path_array) == 1:
            self.up_button.disable()
        else:
            self.up_button.enable()

    def get_selected_path(self) -> str:
        return os.path.join(*self.path_array)
