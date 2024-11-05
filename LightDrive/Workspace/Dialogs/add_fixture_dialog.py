from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QPixmap

class AddFixtureDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AddFixtureDialog")
        self.setWindowTitle("LightDrive - Add Fixture")
        self.channel_data = None

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Workspace/Dialogs/add_fixture_dialog.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        # Add buttons
        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def accept(self):
        super().accept()
