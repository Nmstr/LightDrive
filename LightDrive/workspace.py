from Backend.output import DmxOutput
from Workspace.Widgets.value_slider import ValueSlider
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QFile
import sys

class Workspace(QMainWindow):
    def __init__(self) -> None:
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
        self.setup_console_page()

        # Setup output
        self.dmx_output = DmxOutput('127.0.0.1', 0)
        self.dmx_output.set_single_value(1, 127)

    def show_page(self, page_index: int) -> None:
        """
        Changes the current page in the content_page QStacked widget
        :param page_index: The index of the page to switch to
        :return: None
        """
        self.ui.content_page.setCurrentIndex(page_index)

    def setup_console_page(self) -> None:
        """
        Creates the console page
        :return: None
        """
        console_layout = self.ui.console_scroll_content.layout()
        for i in range(512):
            value_slider = ValueSlider(self, i)
            console_layout.insertWidget(console_layout.count() - 1, value_slider)

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
