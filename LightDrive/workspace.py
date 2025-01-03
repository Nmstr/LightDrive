from workspace_file_manager import WorkspaceFileManager
from Backend.output import DmxOutput
from Functions.snippet_manager import SnippetManager
from LightDrive.Workspace.Dialogs.add_fixture_dialog import AddFixtureDialog
from Workspace.Widgets.value_slider import ValueSlider
from Workspace.Widgets.io_universe_entry import UniverseEntry
from Workspace.Widgets.control_desk import ControlDesk
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QTreeWidgetItem, QSplitter, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QCloseEvent, QPixmap, QAction, QShortcut, QKeySequence
from PySide6.QtCore import QFile, QSize, Qt
import uuid
import sys

class Workspace(QMainWindow):
    def __init__(self) -> None:
        self.universe_entries = {}
        self.selected_universe_entry = None
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
        self.dmx_output = DmxOutput()

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
        self.setObjectName("Workspace")
        self.setWindowTitle("LightDrive - Workspace")

        # Load the stylesheet
        with open('style.qss', 'r') as f:
            app.setStyleSheet(f.read())

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
            self.live_mode = False
            self.ui.toggle_live_mode_btn.setIcon(QPixmap("Assets/Icons/play.svg"))

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
        for i in range(10):
            universe_fixture_item = QTreeWidgetItem()
            universe_fixture_item.setText(0, f"Universe: {i + 1}")
            universe_fixture_item.setIcon(0, QPixmap("Assets/Icons/dmx_port.svg"))
            self.ui.fixture_tree_widget.addTopLevelItem(universe_fixture_item)

    def show_add_fixture_dialog(self) -> None:
        """
        Show the dialog to add a fixture and if successful, add the fixture
        :return: None
        """
        dlg = AddFixtureDialog()
        if not dlg.exec() or not dlg.current_selected_fixture_item:
            return
        fixture_data = dlg.current_selected_fixture_item.extra_data
        amount = dlg.ui.amount_spin.value()
        universe = dlg.ui.universe_combo.currentIndex() + 1
        address = dlg.ui.address_spin.value()
        self.add_fixture(amount, fixture_data, universe, address)

    def add_fixture(self, amount: int, fixture_data: dict, universe: int, address: int, provided_uuid: str = None) -> None:
        """
        Add the fixture
        :param amount: The amount of the fixture
        :param fixture_data: The fixture data
        :param universe: The universe of the fixture
        :param address: The address of the fixture
        :param provided_uuid: The uuid of the fixture (used when loading workspace; defaults to None, setting a new one)
        :return: None
        """
        for _ in range(amount):
            parent_item = self.ui.fixture_tree_widget.topLevelItem(universe - 1)
            parent_item.setExpanded(True)

            fixture_item = QTreeWidgetItem(parent_item)
            fixture_item.setIcon(0, QPixmap(f"Assets/Icons/{fixture_data["light_type"].lower().replace(" ", "_")}.svg"))
            fixture_item.setText(0, fixture_data["name"])
            fixture_universe = universe
            fixture_address = address
            fixture_item.setText(1,
                                 f"{fixture_universe}>{fixture_address}-{fixture_address + len(fixture_data["channels"]) - 1}")
            fixture_uuid = str(uuid.uuid4())
            fixture_item.uuid = provided_uuid if provided_uuid else fixture_uuid
            self.available_fixtures.append({
                "id": fixture_data["id"],
                "name": fixture_data["name"],
                "universe": fixture_universe,
                "address": fixture_address,
                "fixture_uuid": provided_uuid if provided_uuid else fixture_uuid,
            })

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

    def console_set_current_universe(self, universe: int) -> None:
        """
        Changes the current universe displayed in the console tab
        :param universe: The universe to change to
        :return: None
        """
        self.console_current_universe = universe + 1
        for slider in self.value_sliders:
            slider.update_universe()
            slider.update_icon()

    def setup_io_page(self) -> None:
        """
        Creates the io page
        :return: None
        """
        console_layout = self.ui.io_scroll_content.layout()

        for i in range(10):
            universe_entry = UniverseEntry(self, i)
            console_layout.insertWidget(console_layout.count() - 1, universe_entry)
            self.universe_entries[i] = universe_entry

    def select_io_universe(self, universe_number: int) -> None:
        """
        Selects a different universe in the io page
        :param universe_number: The index of the universe to select
        :return: None
        """
        if self.selected_universe_entry:
            self.selected_universe_entry.deselect()
        self.selected_universe_entry = self.universe_entries[universe_number]

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
