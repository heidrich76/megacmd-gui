from nicegui import ui


def create_warning_label(text):
    ui.label(text).classes(
        "text-sm bg-orange-200 text-orange-900 font-semibold px-3 py-1 rounded ml-2"
    )


def add_tabs_style():
    pass
    ui.add_css(
        """
        @media (max-width: 650px) {
            .q-tab {
                padding-left: 0.25rem;
                padding-right: 0.25rem;
            }
            .q-tab__label {
                display: none;
            }
        }
        """
    )


def create_tab(name, label, icon):
    ui.tab(name=name, label=label, icon=icon).props("no-caps")


def create_action_table(columns, rows, callback, icon="info"):
    columns.append(
        {"name": "action", "label": "ACTION", "field": "action", "sortable": False}
    )
    table = ui.table(columns=columns, rows=rows)
    table.add_slot(
        "body-cell-action",
        f"""
            <q-td :props="props">
                <q-btn icon="{icon}" flat dense @click="$parent.$emit('action', props)" />
            </q-td>
        """,
    )
    table.on("action", lambda msg: callback(msg.args["row"]))
    return table
