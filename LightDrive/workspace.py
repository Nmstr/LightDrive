from workspace_file_manager import WorkspaceFileManager
from Backend.output import DmxOutput
from Settings.settings import SettingsDialog
from Functions.snippet_manager import SnippetManager
from Workspace.Dialogs.add_fixture_dialog import AddFixtureDialog
from Workspace.Widgets.value_slider import ValueSlider
from Workspace.Widgets.io_universe_entry import UniverseEntry
from Workspace.Widgets.control_desk import ControlDesk
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QTreeWidgetItem, QSplitter, QMessageBox, \
    QListWidgetItem, QInputDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QCloseEvent, QPixmap, QAction, QShortcut, QKeySequence
from PySide6.QtCore import QFile, QSize, Qt
import configparser
import uuid
import json
import sys
import os

class Workspace(QMainWindow):
    def __init__(self) -> None:
        self.console_current_universe = 1
        self.value_sliders = []
        self.available_fixtures =  []
        self.control_desk_view = None
        self.live_mode = False
        self.snippet_manager = SnippetManager(self)
        super().__init__()

        self.setup_main_window()
        # Setup pages
        self.setup_fixture_page()
        self.setup_console_page()
        self.setup_io_page()
        self.setup_snippet_page()
        self.setup_control_desk_page()

        # Setup hotkeys
        self.save_hotkey = QShortcut(QKeySequence.Save, self)
        self.save_hotkey.activated.connect(lambda: self.workspace_file_manager.save_workspace())

        # Setup output
        self.dmx_output = DmxOutput(self)

        self.workspace_file_manager = WorkspaceFileManager(self, app, EXIT_CODE_REBOOT, current_workspace_file)
        # Open any workspace if rebooted after workspace was opened
        if current_workspace_file:  # current_workspace_file is the path to the workspace to open or None
            self.workspace_file_manager.open_workspace(current_workspace_file)

        self.show()

    def setup_main_window(self) -> None:
        """
        Sets up the main window
        :return: None
        """
        self.setWindowTitle("LightDrive - Workspace")

        # Set the theme
        if os.path.isdir("/usr/lib/qt6/plugins"):
            app.addLibraryPath("/usr/lib/qt6/plugins")
        config = configparser.ConfigParser()
        config.read(os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/settings.ini')
        if "Settings" in config:
            app.setStyle(config["Settings"].get("theme", "Breeze"))

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Workspace/workspace.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())
        self.showMaximized()

        # Create a menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        # Add File entry
        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)
        new_action = QAction("New", self)
        new_action.setIcon(QPixmap("Assets/Icons/new.svg"))
        file_menu.addAction(new_action)
        new_action.triggered.connect(lambda: self.workspace_file_manager.new_workspace())
        open_action = QAction("Open", self)
        open_action.setIcon(QPixmap("Assets/Icons/open.svg"))
        file_menu.addAction(open_action)
        open_action.triggered.connect(lambda: self.workspace_file_manager.show_open_workspace_dialog())
        save_action = QAction("Save", self)
        save_action.setIcon(QPixmap("Assets/Icons/save.svg"))
        file_menu.addAction(save_action)
        save_action.triggered.connect(lambda: self.workspace_file_manager.save_workspace())
        save_as_action = QAction("Save As", self)
        save_as_action.setIcon(QPixmap("Assets/Icons/save_as.svg"))
        file_menu.addAction(save_as_action)
        save_as_action.triggered.connect(lambda: self.workspace_file_manager.save_workspace_as())
        # Add Settings entry
        settings_menu = QMenu("Settings", self)
        menu_bar.addMenu(settings_menu)
        preferences_action = QAction("Preferences", self)
        settings_menu.addAction(preferences_action)
        preferences_action.triggered.connect(self.show_settings)

        # Configure buttons
        self.ui.fixture_btn.clicked.connect(lambda: self.show_page(0))
        self.ui.fixture_btn.setIcon(QPixmap("Assets/Icons/fixture_page.svg"))
        self.ui.fixture_btn.setIconSize(QSize(24, 24))
        self.ui.console_btn.clicked.connect(lambda: self.show_page(1))
        self.ui.console_btn.setIcon(QPixmap("Assets/Icons/console_page.svg"))
        self.ui.console_btn.setIconSize(QSize(24, 24))
        self.ui.io_btn.clicked.connect(lambda: self.show_page(2))
        self.ui.io_btn.setIcon(QPixmap("Assets/Icons/io_page.svg"))
        self.ui.io_btn.setIconSize(QSize(24, 24))
        self.ui.snippet_btn.clicked.connect(lambda: self.show_page(3))
        self.ui.snippet_btn.setIcon(QPixmap("Assets/Icons/snippet_page.svg"))
        self.ui.snippet_btn.setIconSize(QSize(24, 24))
        self.ui.control_desk_btn.clicked.connect(lambda: self.show_page(4))
        self.ui.control_desk_btn.setIcon(QPixmap("Assets/Icons/control_desk_page.svg"))
        self.ui.control_desk_btn.setIconSize(QSize(24, 24))

        self.ui.toggle_live_mode_btn.clicked.connect(self.toggle_live_mode)
        self.ui.toggle_live_mode_btn.setIcon(QPixmap("Assets/Icons/play.svg"))

    def toggle_live_mode(self) -> None:
        """
        Toggles whether live mode in enabled or disabled
        :return: None
        """
        if self.ui.toggle_live_mode_btn.isChecked():
            self.live_mode = True
            self.ui.toggle_live_mode_btn.setIcon(QPixmap("Assets/Icons/stop.svg"))
        else:
            if self.control_desk_view.has_active_item():  # Ask for confirmation, if at least one item is active on the desk
                disable_live_dialog = QMessageBox()
                disable_live_dialog.setWindowTitle("LightDrive - Disable Live Mode")
                disable_live_dialog.setText("There is at least one item active on the desk.\nDo you really want to disable live mode? This will stop all running items.")
                disable_live_dialog.addButton(QMessageBox.Yes)
                disable_live_dialog.addButton(QMessageBox.No)
                if disable_live_dialog.exec() == QMessageBox.No:  # Cancel disabling of live mode, if no
                    return
            self.control_desk_view.disable_all_items()
            self.live_mode = False
            self.ui.toggle_live_mode_btn.setIcon(QPixmap("Assets/Icons/play.svg"))

    def show_settings(self) -> None:
        """
        Shows the settings dialog
        :return: None
        """
        settings = SettingsDialog()
        settings.exec()

    def show_page(self, page_index: int) -> None:
        """
        Changes the current page in the content_page QStacked widget
        :param page_index: The index of the page to switch to
        :return: None
        """
        self.ui.content_page.setCurrentIndex(page_index)

    def setup_fixture_page(self) -> None:
        """
        Creates the fixture page
        :return: None
        """
        self.ui.fixture_add_btn.clicked.connect(self.show_add_fixture_dialog)
        self.ui.fixture_add_btn.setIcon(QPixmap("Assets/Icons/add.svg"))
        self.ui.fixture_remove_btn.clicked.connect(self.remove_fixture)
        self.ui.fixture_remove_btn.setIcon(QPixmap("Assets/Icons/remove.svg"))

    def show_add_fixture_dialog(self) -> None:
        """
        Show the dialog to add a fixture and if successful, add the fixture
        :return: None
        """
        dlg = AddFixtureDialog(self)
        if not dlg.exec() or not dlg.current_selected_fixture_item:
            return
        fixture_data = dlg.current_selected_fixture_item.extra_data
        amount = dlg.ui.amount_spin.value()
        universe_uuid = dlg.ui.universe_combo.currentData()
        address = dlg.ui.address_spin.value()
        self.add_fixture(amount, fixture_data, universe_uuid, address)

    def fixture_display_items(self):
        """
        Displays all fixtures in the fixture tree widget
        :return: None
        """
        self.ui.fixture_tree_widget.clear()
        # Display all universes
        universe_configuration = self.dmx_output.get_configuration()
        for universe_uuid, universe_data in universe_configuration.items():
            universe_fixture_item = QTreeWidgetItem()
            universe_fixture_item.setText(0, universe_data["name"])
            universe_fixture_item.setIcon(0, QPixmap("Assets/Icons/dmx_port.svg"))
            universe_fixture_item.universe_uuid = universe_uuid
            self.ui.fixture_tree_widget.addTopLevelItem(universe_fixture_item)

        # Display all fixtures
        for fixture in self.available_fixtures:
            # Load fixture data
            fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
            with open(os.path.join(fixture_dir, fixture["id"] + ".json")) as f:
                fixture_data = json.load(f)
            # Find the parent item
            parent_item = None
            for item_index in range(self.ui.fixture_tree_widget.topLevelItemCount()):
                item = self.ui.fixture_tree_widget.topLevelItem(item_index)
                if item.universe_uuid == fixture.get("universe"):
                    parent_item = item
                    break
            # Inform the user if the parent item could not be found
            if not parent_item:
                parent_error = QMessageBox()
                parent_error.setWindowTitle("LightDrive - Error")
                parent_error.setText(f"Could not find parent item for fixture {fixture['name']}.")
                parent_error.setInformativeText("Please check your fixture configuration.")
                parent_error.exec()
                continue
            # Add the fixture item
            parent_item.setExpanded(True)
            fixture_item = QTreeWidgetItem(parent_item)
            fixture_item.setIcon(0, QPixmap(f"Assets/Icons/{fixture_data["light_type"].lower().replace(" ", "_")}.svg"))
            fixture_item.setText(0, fixture["name"])
            fixture_item.setText(1, f"{universe_configuration[fixture['universe']]["name"]}>{fixture['address']}-{fixture['address'] + len(fixture_data["channels"]) - 1}")
            fixture_item.uuid = fixture["fixture_uuid"]

    def add_fixture(self, amount: int, fixture_data: dict, universe_uuid: str, address: int, provided_uuid: str = None) -> None:
        """
        Add the fixture
        :param amount: The amount of the fixture
        :param fixture_data: The fixture data
        :param universe_uuid: The universe of the fixture
        :param address: The address of the fixture
        :param provided_uuid: The uuid of the fixture (used when loading workspace; defaults to None, setting a new one)
        :return: None
        """
        for _ in range(amount):
            fixture_uuid = str(uuid.uuid4())
            self.available_fixtures.append({
                "id": fixture_data["id"],
                "name": fixture_data["name"],
                "universe": universe_uuid,
                "address": address,
                "fixture_uuid": provided_uuid if provided_uuid else fixture_uuid,
            })
        self.fixture_display_items()

    def remove_fixture(self) -> None:
        """
        Removes a fixture from the workspace
        :return: None
        """
        current_item = self.ui.fixture_tree_widget.selectedItems()[0]
        for fixture in self.available_fixtures:
            if current_item.uuid == fixture["fixture_uuid"]:
                self.available_fixtures.remove(fixture)
        current_item.parent().removeChild(current_item)

    def setup_console_page(self) -> None:
        """
        Creates the console page
        :return: None
        """
        self.ui.console_current_universe_combo.currentIndexChanged.connect(self.console_set_current_universe)
        console_layout = self.ui.console_scroll_content.layout()
        for i in range(512):
            value_slider = ValueSlider(self, i)
            console_layout.insertWidget(console_layout.count() - 1, value_slider)
            self.value_sliders.append(value_slider)

    def console_set_current_universe(self) -> None:
        """
        Changes the current universe displayed in the console tab
        :return: None
        """
        self.console_current_universe = self.ui.console_current_universe_combo.currentData()
        for slider in self.value_sliders:
            slider.update_universe()
            slider.update_icon()

    def console_display_universes(self) -> None:
        """
        Updates the universe combo box in the console tab to display all available universes
        :return: None
        """
        self.ui.console_current_universe_combo.clear()
        for universe_uuid, universe_data in self.dmx_output.get_configuration().items():
            self.ui.console_current_universe_combo.addItem(universe_data["name"], universe_uuid)

    def setup_io_page(self) -> None:
        """
        Creates the io page
        :return: None
        """
        self.ui.io_add_universe_btn.clicked.connect(self.io_add_universe)
        self.ui.io_add_universe_btn.setIcon(QPixmap("Assets/Icons/add.svg"))
        self.ui.io_remove_universe_btn.clicked.connect(self.io_remove_universe)
        self.ui.io_remove_universe_btn.setIcon(QPixmap("Assets/Icons/remove.svg"))

    def io_add_universe(self, universe_uuid: str) -> None:
        """
        Creates a new universe and adds it to the io page
        :param universe_uuid: The uuid of the universe (generates a new one if not provided)
        :return: None
        """
        creation_dlg = QInputDialog()
        creation_dlg.setWindowTitle("LightDrive - Add Universe")
        creation_dlg.setLabelText("Enter the name of the universe:")
        creation_dlg.setInputMode(QInputDialog.TextInput)
        creation_dlg.setOkButtonText("Add")
        creation_dlg.setCancelButtonText("Cancel")
        if not creation_dlg.exec():
            return  # Cancelled
        universe_name = creation_dlg.textValue()
        if not universe_name:
            no_name_dlg = QMessageBox()
            no_name_dlg.setWindowTitle("LightDrive - Error")
            no_name_dlg.setText("You need to supply a name for the universe.")
            no_name_dlg.exec()
            return  # No name supplied
        if not universe_uuid:  # Generate a new uuid if not provided
            universe_uuid = str(uuid.uuid4())
        # Add the universe
        self.dmx_output.create_universe(universe_uuid, universe_name)
        self.io_add_universe_entry(universe_uuid, universe_name)
        self.fixture_display_items()
        self.console_display_universes()

    def io_add_universe_entry(self, universe_uuid: str, universe_name: str) -> None:
        """
        Adds a universe entry in the io tab
        :param universe_uuid: The uuid of the universe
        :param universe_name: The name of the universe
        :return: None
        """
        item = QListWidgetItem(self.ui.io_universe_list)
        universe_entry = UniverseEntry(self, universe_uuid, universe_name)
        item.setSizeHint(universe_entry.sizeHint())
        self.ui.io_universe_list.setItemWidget(item, universe_entry)

    def io_remove_universe(self) -> None:
        """
        Removes a universe
        :return: None
        """
        current_item = self.ui.io_universe_list.selectedItems()[0]
        for universe in self.dmx_output.get_configuration():
            widget = self.ui.io_universe_list.itemWidget(current_item)
            if widget.universe_uuid == universe:
                self.dmx_output.remove_universe(universe)
        self.fixture_display_items()
        self.ui.io_universe_list.takeItem(self.ui.io_universe_list.row(current_item))
        self.console_display_universes()

    def setup_snippet_page(self) -> None:
        """
        Creates the snippet page
        :return: None
        """
        # Replace the ui.snippet_lower frame with a splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.ui.snippet_selector_tree)
        splitter.addWidget(self.ui.snippet_editor)
        self.ui.snippet_lower.layout().addWidget(splitter)

        self.ui.snippet_selector_tree.itemActivated.connect(self.snippet_manager.show_editor)

        self.ui.cue_btn.clicked.connect(self.snippet_manager.create_cue)
        self.ui.cue_btn.setIcon(QPixmap("Assets/Icons/cue.svg"))
        self.ui.scene_btn.clicked.connect(self.snippet_manager.create_scene)
        self.ui.scene_btn.setIcon(QPixmap("Assets/Icons/scene.svg"))
        self.ui.efx_2d_btn.clicked.connect(self.snippet_manager.create_efx_2d)
        self.ui.efx_2d_btn.setIcon(QPixmap("Assets/Icons/efx_2d.svg"))
        self.ui.rgb_matrix_btn.clicked.connect(self.snippet_manager.create_rgb_matrix)
        self.ui.rgb_matrix_btn.setIcon(QPixmap("Assets/Icons/rgb_matrix.svg"))
        self.ui.script_btn.clicked.connect(self.snippet_manager.create_script)
        self.ui.script_btn.setIcon(QPixmap("Assets/Icons/script.svg"))
        self.ui.directory_btn.clicked.connect(self.snippet_manager.create_dir)
        self.ui.directory_btn.setIcon(QPixmap("Assets/Icons/directory.svg"))

        self.ui.scene_add_fixture.clicked.connect(self.snippet_manager.scene_add_fixture)
        self.ui.scene_add_fixture.setIcon(QPixmap("Assets/Icons/add.svg"))
        self.ui.scene_remove_fixture.clicked.connect(self.snippet_manager.scene_remove_fixture)
        self.ui.scene_remove_fixture.setIcon(QPixmap("Assets/Icons/remove.svg"))
        self.ui.scene_name_edit.editingFinished.connect(self.snippet_manager.rename_scene)
        self.ui.scene_show_btn.clicked.connect(self.snippet_manager.scene_toggle_show)
        self.ui.scene_show_btn.setIcon(QPixmap("Assets/Icons/show_output.svg"))

        self.ui.cue_name_edit.editingFinished.connect(self.snippet_manager.rename_cue)
        self.ui.cue_add_fixture.clicked.connect(self.snippet_manager.cue_add_fixture)
        self.ui.cue_add_fixture.setIcon(QPixmap("Assets/Icons/add.svg"))
        self.ui.cue_play_btn.clicked.connect(self.snippet_manager.cue_play)
        self.ui.cue_play_btn.setIcon(QPixmap("Assets/Icons/play.svg"))
        self.ui.cue_pause_btn.clicked.connect(self.snippet_manager.cue_pause)
        self.ui.cue_pause_btn.setIcon(QPixmap("Assets/Icons/pause.svg"))
        self.ui.cue_stop_btn.clicked.connect(self.snippet_manager.cue_stop)
        self.ui.cue_stop_btn.setIcon(QPixmap("Assets/Icons/stop.svg"))

        self.ui.directory_name_edit.editingFinished.connect(self.snippet_manager.rename_dir)

    def setup_control_desk_page(self) -> None:
        """
        Creates the control desk page
        :return: None
        """
        self.control_desk_view = ControlDesk(self)
        self.ui.control_desk_content_frame.layout().addWidget(self.control_desk_view)

        self.ui.desk_add_btn.clicked.connect(self.control_desk_view.add_btn)
        self.ui.desk_add_btn.setIcon(QPixmap("Assets/Icons/desk_button.svg"))
        self.ui.desk_add_fader.clicked.connect(self.control_desk_view.add_fader)
        self.ui.desk_add_fader.setIcon(QPixmap("Assets/Icons/desk_fader.svg"))
        self.ui.desk_add_knob.clicked.connect(self.control_desk_view.add_knob)
        self.ui.desk_add_knob.setIcon(QPixmap("Assets/Icons/desk_knob.svg"))
        self.ui.desk_add_sound_trigger.clicked.connect(self.control_desk_view.add_sound_trigger)
        self.ui.desk_add_sound_trigger.setIcon(QPixmap("Assets/Icons/desk_sound_trigger.svg"))
        self.ui.desk_add_label.clicked.connect(self.control_desk_view.add_label)
        self.ui.desk_add_label.setIcon(QPixmap("Assets/Icons/desk_label.svg"))
        self.ui.desk_add_clock.clicked.connect(self.control_desk_view.add_clock)
        self.ui.desk_add_clock.setIcon(QPixmap("Assets/Icons/desk_clock.svg"))

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """
        Handles closing of the application
        :param event:  The close event
        :return: None
        """
        if self.live_mode:
            event.ignore()
            error_message = QMessageBox()
            error_message.setWindowTitle("LightDrive - Error")
            error_message.setText("LightDrive can not be closed while in live mode. Please change back to design mode first.")
            error_message.exec()
            return
        self.dmx_output.shutdown_output()
        super().closeEvent(event)

if __name__ == "__main__":
    current_workspace_file = None
    EXIT_CODE_REBOOT = -123987123
    exit_code = EXIT_CODE_REBOOT  # Execute at least once
    while exit_code == EXIT_CODE_REBOOT:
        app = QApplication(sys.argv)
        window = Workspace()
        exit_code = app.exec()
        app.shutdown()
        current_workspace_file = window.workspace_file_manager.current_workspace_file
    sys.exit(exit_code)
