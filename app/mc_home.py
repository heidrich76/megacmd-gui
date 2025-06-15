from nicegui import ui
from mc_layout import create_warning_label


def home_page():
    ui.page_title("Home")

    ui.label("Home").classes("text-h5")
    ui.add_css(
        """
.nicegui-markdown a, .nicegui-markdown a:visited {
    color: grey;
    text-decoration: none;
}
.nicegui-markdown a:hover {
    color: grey;
    text-decoration: underline;
}
"""
    )
    ui.markdown(
        """
This app provides a simple web-based user interface for <a href="https://github.com/meganz/MEGAcmd" target="_blank">MEGAcmd</a>.
It allows using MEGAcmd for synchronizing your files with the <a href="https://mega.nz/" target="_blank">MEGA cloud</a>.

**Features**

- **Logging In:** Authenticate and gain access to your MEGA account within the web interface.
- **File and Folder Synchronization:** Manage active synchronization tasks between local directories and your MEGA cloud storage.
- **WebDAV Access:** Potentially expose your MEGA cloud storage via WebDAV for integration with other applications or file managers.
- **Backup Management:** Dedicated functionality for creating and managing backups to your MEGA cloud storage.
- **Cloud Drive Mounting:** Mount your MEGA cloud storage as a local filesystem for seamless access through your operating system's file explorer.
- **Integrated Terminal Access:** Provides direct command-line access to MegaCMD for advanced operations and scripting within the web interface.
- Complete MEGAcmd user guide is available <a href="https://github.com/meganz/MEGAcmd/blob/master/UserGuide.md" target="_blank">here</a>.
"""
    )
    create_warning_label("This add-on is provided as-is. Use at your own risk.")
