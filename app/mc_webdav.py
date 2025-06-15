from nicegui import app, ui
from mc_directories import DirectorySelector
from mc_subprocess import list_webdavs, add_webdav, remove_webdav


@ui.refreshable
def create_webdav_table():
    base_url = app.storage.general.get("webdav_base_url", "")
    columns, rows, local_paths = list_webdavs(base_url)

    with ui.row().classes("w-full overflow-auto"):
        table = ui.table(columns=columns, rows=rows).classes("w-full")
        table.add_slot(
            "body-cell-URL",
            """
                    <q-td :props="props">
                        <a :href="props.value" target="_blank">{{ props.value }}</a>
                    </q-td>
                """,
        )

    ui.input(label="Base URL").classes("w-full").bind_value(
        app.storage.general, "webdav_base_url"
    )

    # Add dialog
    with ui.dialog() as serve_dialog, ui.card():
        ui.label("Serve WebDAV Path").classes("text-lg font-bold")
        remote_path_input = DirectorySelector("REMOTEPATH", "/", is_remote=True)
        ui.checkbox(text="Start with public option").bind_value(
            app.storage.general, "webdav_is_public"
        )

        with ui.row():
            ui.button("Cancel", on_click=serve_dialog.close)

            def on_serve():
                remote_path = remote_path_input.get_selected_path()
                is_public = app.storage.general.get("webdav_is_public", False)
                add_webdav(remote_path, is_public)
                serve_dialog.close()
                create_webdav_table.refresh()

            ui.button("OK", on_click=on_serve)

    # Delete dialog
    with ui.dialog() as unserve_dialog, ui.card():
        ui.label("Unserve WebDAV Path").classes("text-lg font-bold")
        path_select = ui.select(local_paths, label="Path").classes("w-full")

        with ui.row():
            ui.button("Cancel", on_click=unserve_dialog.close)

            def on_unserve():
                remote_path = path_select.value
                remove_webdav(remote_path)
                unserve_dialog.close()
                create_webdav_table.refresh()

            ui.button("OK", color="red", on_click=on_unserve)

    def open_serve_dialog():
        serve_dialog.open()

    def open_unserve_dialog():
        unserve_dialog.open()

    with ui.row():
        ui.button(icon="add", on_click=serve_dialog.open).classes("mt-6")
        ui.button(icon="delete", on_click=unserve_dialog.open).classes("mt-6")
        ui.button(icon="refresh", on_click=create_webdav_table.refresh).classes("mt-6")


def webdav_page():
    ui.page_title("WebDAV")

    with ui.column().classes("w-full"):
        ui.label("WebDAV").classes("text-h5")
        ui.label("Currently served WebDAV folders")
        create_webdav_table()
