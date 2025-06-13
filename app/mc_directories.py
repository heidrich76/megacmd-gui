from nicegui import ui
import os
from mc_subprocess import ls, mkdir


class DirectorySelector:
    def __init__(self, title: str, start_path: str = "/", is_remote=False):
        self._path_array = [start_path.rstrip("/")] if start_path != "/" else ["/"]
        self._path = self.get_selected_path()
        self._path_label = None
        self._select_box = None
        self._up_button = None
        self._is_remote = is_remote
        self._build_ui(title)

    def _build_ui(self, title):
        with ui.column().classes("p-4 border rounded shadow-md w-full"):
            ui.label(title).classes("text-lg font-bold")
            with ui.row():
                ui.label("Path:").classes("font-bold")
                self._path_label = ui.label("/")
            self._select_box = ui.select(options=[], label="Sub-folders").classes(
                "w-full"
            )

            def go_down():
                if self._select_box.value:
                    self._path_array.append(self._select_box.value)
                    self._refresh_ui()

            def go_up():
                if len(self._path_array) > 1:
                    self._path_array.pop()
                    self._refresh_ui()

            self._select_box.on("update:model-value", go_down)
            with ui.row():
                self._up_button = ui.button(icon="arrow_upward", on_click=go_up).props(
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
                        mkdir(self._path, new_dir, self._is_remote)
                        self._refresh_ui()

                    ui.button(icon="add", on_click=on_add).props("dense flat")
        self._refresh_ui()

    def _refresh_ui(self):
        self._path = self.get_selected_path()
        self._path_label.text = self._path

        subdirs = ls(self._path, self._is_remote)
        self._select_box.set_options(subdirs)
        if len(subdirs) == 0:
            self._select_box.disable()
        else:
            self._select_box.enable()
        self._select_box.value = None

        if len(self._path_array) == 1:
            self._up_button.disable()
        else:
            self._up_button.enable()

    def get_selected_path(self) -> str:
        return os.path.join(*self._path_array)
