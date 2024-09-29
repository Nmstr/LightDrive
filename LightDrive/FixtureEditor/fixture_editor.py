from channel_entry import ChannelEntry
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("FixtureEditor")
        self.setWindowTitle("LightDrive")
        self.channels = []

        # Load the stylesheet
        with open('style.qss', 'r') as f:
            app.setStyleSheet(f.read())

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("FixtureEditor/fixture_editor.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        self.ui.add_channel_btn.clicked.connect(self.add_channel)

    def add_channel(self):
        layout = self.ui.channel_container.layout()
        channel_entry = ChannelEntry()
        layout.insertWidget(layout.count() - 1, channel_entry)
        self.channels.append(channel_entry)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
