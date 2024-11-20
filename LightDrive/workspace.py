from workspace_file_manager import write_workspace_file, read_workspace_file
from Backend.output import DmxOutput
from LightDrive.Workspace.Dialogs.add_fixture_dialog import AddFixtureDialog
from Workspace.Widgets.value_slider import ValueSlider
from Workspace.Widgets.io_universe_entry import UniverseEntry
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QTreeWidgetItem, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QCloseEvent, QPixmap, QAction, QShortcut, QKeySequence
from PySide6.QtCore import QFile
import json
import uuid
import sys
import os

class Workspace(QMainWindow):
    def __init__(self) -> None:
        self.universe_entries = {}
        self.selected_universe_entry = None
        self.console_current_universe = 1
        self.value_sliders = []
        self.available_fixtures =  []
        self.current_snippet = None
        super().__init__()

        self.setup_main_window()
        # Setup pages
        self.setup_fixture_page()
        self.setup_console_page()
        self.setup_io_page()
        self.setup_snippet_page()

        # Setup hotkeys
        self.save_hotkey = QShortcut(QKeySequence.Save, self)
        self.save_hotkey.activated.connect(lambda: self.save_workspace())

        # Setup output
        self.dmx_output = DmxOutput()

        # Open any workspace if rebooted after workspace was opened
        if current_workspace_file:  # current_workspace_file is the path to the workspace to open or None
            self.open_workspace(current_workspace_file)

        self.show()

    def setup_main_window(self):
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
        file_menu.addAction(new_action)
        new_action.triggered.connect(lambda: self.new_workspace())
        open_action = QAction("Open", self)
        file_menu.addAction(open_action)
        open_action.triggered.connect(lambda: self.show_open_workspace_dialog())
        save_action = QAction("Save", self)
        file_menu.addAction(save_action)
        save_action.triggered.connect(lambda: self.save_workspace())
        save_as_action = QAction("Save As", self)
        file_menu.addAction(save_as_action)
        save_as_action.triggered.connect(lambda: self.save_workspace_as())

        # Connect buttons
        self.ui.fixture_btn.clicked.connect(lambda: self.show_page(0))
        self.ui.console_btn.clicked.connect(lambda: self.show_page(1))
        self.ui.io_btn.clicked.connect(lambda: self.show_page(2))
        self.ui.snippet_btn.clicked.connect(lambda: self.show_page(3))

    def new_workspace(self):
        global current_workspace_file
        current_workspace_file = None
        app.exit(EXIT_CODE_REBOOT)

    def save_workspace_as(self):
        dlg = QFileDialog(self, directory=os.path.expanduser("~"))
        dlg.setNameFilter("Workspace (*.ldw)")
        dlg.setDefaultSuffix(".ldw")
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        if dlg.exec():
            filename = dlg.selectedFiles()[0]
            global current_workspace_file
            current_workspace_file = filename
            self.save_workspace()

    def save_workspace(self):
        global current_workspace_file
        if not current_workspace_file:
            self.save_workspace_as()
        else:
            write_workspace_file(workspace_file_path=current_workspace_file,
                                 fixtures=self.available_fixtures,
                                 dmx_output_configuration=self.dmx_output.output_configuration)

    def show_open_workspace_dialog(self):
        dlg = QFileDialog(self, directory=os.path.expanduser("~"))
        dlg.setNameFilter("Workspace (*.ldw)")
        dlg.setDefaultSuffix(".ldw")
        dlg.setFileMode(QFileDialog.ExistingFile)
        if dlg.exec():
            global current_workspace_file
            current_workspace_file = dlg.selectedFiles()[0]
            app.exit(EXIT_CODE_REBOOT)  # Restart application (opens workspace while opening)

    def open_workspace(self, workspace_file_path):
        fixtures, dmx_output_configuration = read_workspace_file(workspace_file_path)
        # Add the fixtures
        for fixture in fixtures:
            # Read the fixture data
            fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
            with open(os.path.join(fixture_dir, fixture["id"] + ".json")) as f:
                fixture_data = json.load(f)
            # Add the fixture
            self.add_fixture(amount = 1,
                             fixture_data = fixture_data,
                             universe = fixture["universe"],
                             address = fixture["address"])
        # Configure the dmx output
        self.dmx_output.write_universe_configuration(dmx_output_configuration)

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
        self.ui.fixture_remove_btn.clicked.connect(self.remove_fixture)
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

    def add_fixture(self, amount, fixture_data, universe, address) -> None:
        """
        Add the fixture
        :param amount: The amount of the fixture
        :param fixture_data: The fixture data
        :param universe: The universe of the fixture
        :param address: The address of the fixture
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
            fixture_item.uuid = fixture_uuid
            self.available_fixtures.append({
                "id": fixture_data["id"],
                "name": fixture_data["name"],
                "universe": fixture_universe,
                "address": fixture_address,
                "fixture_uuid": fixture_uuid,
            })

    def remove_fixture(self) -> None:
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
        self.ui.snippet_selector_tree.itemActivated.connect(self.snippet_show_editor)

        self.ui.cue_btn.clicked.connect(lambda: print("cue"))
        self.ui.scene_btn.clicked.connect(lambda: print("scene"))
        self.ui.efx_2d_btn.clicked.connect(lambda: print("2d efx"))
        self.ui.rgb_matrix_btn.clicked.connect(lambda: print("rgb matrix"))
        self.ui.script_btn.clicked.connect(lambda: print("script"))
        self.ui.directory_btn.clicked.connect(self.snippet_create_dir)

        self.ui.directory_name_edit.editingFinished.connect(self.snippet_rename_dir)

    def snippet_create_dir(self) -> None:
        """
        Creates a directory in the snippet selector tree
        :return: None
        """
        selector_tree = self.ui.snippet_selector_tree
        new_dir = QTreeWidgetItem()
        new_dir.setIcon(0, QPixmap("Assets/Icons/directory.svg"))
        new_dir.setText(0, "New Directory")
        new_dir.extra_data = {
            "type": "directory",
            "uuid": str(uuid.uuid4()),
            "name": "New Directory",
        }
        if selector_tree.selectedItems():
            selector_tree.selectedItems()[0].addChild(new_dir)
            selector_tree.selectedItems()[0].setExpanded(True)
        else:
            selector_tree.addTopLevelItem(new_dir)

    def snippet_rename_dir(self) -> None:
        """
        Renames the directory to the new name
        :return: None
        """
        self.current_snippet.extra_data["name"] = self.ui.directory_name_edit.text()
        self.current_snippet.setText(0, self.ui.directory_name_edit.text())

    def snippet_show_editor(self, item) -> None:
        match item.extra_data["type"]:
            case "directory":
                self.ui.snippet_editor.setCurrentIndex(1)
                self.ui.directory_name_edit.setText(item.extra_data["name"])
        self.current_snippet = item

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """
        Handles closing of the application
        :param event:  The close event
        :return: None
        """
        self.dmx_output.stop()
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
    sys.exit(exit_code)
