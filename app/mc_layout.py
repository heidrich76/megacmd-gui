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
