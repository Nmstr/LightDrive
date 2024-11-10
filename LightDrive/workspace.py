from Backend.output import DmxOutput
from LightDrive.Workspace.Dialogs.add_fixture_dialog import AddFixtureDialog
from Workspace.Widgets.value_slider import ValueSlider
from Workspace.Widgets.io_universe_entry import UniverseEntry
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtCore import QFile
import sys

class Workspace(QMainWindow):
    def __init__(self) -> None:
        self.universe_entries = {}
        self.selected_universe_entry = None
        self.console_current_universe = 1
        self.value_sliders = []
        self.available_fixtures =  []
        super().__init__()
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

        self.ui.fixture_btn.clicked.connect(lambda: self.show_page(0))
        self.ui.console_btn.clicked.connect(lambda: self.show_page(1))
        self.ui.io_btn.clicked.connect(lambda: self.show_page(2))

        # Setup pages
        self.setup_fixture_page()
        self.setup_console_page()
        self.setup_io_page()

        # Setup output
        self.dmx_output = DmxOutput()

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
        self.ui.fixture_add_btn.clicked.connect(self.add_fixture)
        for i in range(10):
            universe_fixture_item = QTreeWidgetItem()
            universe_fixture_item.setText(0, f"Universe: {i + 1}")
            universe_fixture_item.setIcon(0, QPixmap("Assets/Icons/dmx_port.svg"))
            self.ui.fixture_tree_widget.addTopLevelItem(universe_fixture_item)

    def add_fixture(self) -> None:
        """
        Show the dialog to add a fixture and if successful, add the fixture
        :return: None
        """
        dlg = AddFixtureDialog()
        if not dlg.exec() or not dlg.current_selected_fixture_item:
            return
        fixture_data = dlg.current_selected_fixture_item.extra_data
        parent_item = self.ui.fixture_tree_widget.topLevelItem(dlg.ui.universe_combo.currentIndex())
        parent_item.setExpanded(True)
        for _ in range(dlg.ui.amount_spin.value()):
            fixture_item = QTreeWidgetItem(parent_item)
            fixture_item.setIcon(0, QPixmap(f"Assets/Icons/{fixture_data["light_type"].lower().replace(" ", "_")}.svg"))
            fixture_item.setText(0, fixture_data["name"])
            fixture_universe = dlg.ui.universe_combo.currentIndex() + 1
            fixture_address = dlg.ui.address_spin.value()
            fixture_item.setText(1, f"{fixture_universe}>{fixture_address}-{fixture_address + len(fixture_data["channels"]) - 1}")
            self.available_fixtures.append({
                "id": fixture_data["id"],
                "name": fixture_data["name"],
                "universe": fixture_universe,
                "address": fixture_address
            })

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

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """
        Handles closing of the application
        :param event:  The close event
        :return: None
        """
        self.dmx_output.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Workspace()
    window.show()
    sys.exit(app.exec())
