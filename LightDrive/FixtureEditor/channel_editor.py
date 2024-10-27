from audioop import reverse
from logging import warning
from mmap import error

from PySide6.QtWidgets import QDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QIcon, QPixmap

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtGui import QPixmap

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

class AcceptInfoDialog(QDialog):
    def __init__(self, message: str, *, error_message: bool = True) -> None:
        super().__init__()
        if error_message:
            self.setWindowTitle("Error Saving Channel")
            self.setFixedSize(500, 100)
        else:
            self.setWindowTitle("Info")
            self.setFixedSize(600, 100)

        qbtn = (
            QDialogButtonBox.Ok
        )

        self.buttonBox = QDialogButtonBox(qbtn)
        self.buttonBox.clicked.connect(self.accept)

        layout = QVBoxLayout()
        self.label = QLabel(message, self)
        layout.addWidget(self.label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class ChannelEditor(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ChannelEditor")
        self.setWindowTitle("LightDrive - Channel Editor")
        self.channel_data = None

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("FixtureEditor/channel_editor.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        self.ui.channel_table.setHorizontalHeaderLabels(["Minimum Value", "Maximum Value", "Description"])
        self.ui.channel_table.itemChanged.connect(self.check_and_add_row)

        # Load icons
        self.ui.type_combo.setItemIcon(0, QPixmap("Assets/Icons/intensity.svg"))
        self.ui.type_combo.setItemIcon(1, QPixmap("Assets/Icons/color.svg"))
        self.ui.type_combo.setItemIcon(2, QPixmap("Assets/Icons/red.svg"))
        self.ui.type_combo.setItemIcon(3, QPixmap("Assets/Icons/green.svg"))
        self.ui.type_combo.setItemIcon(4, QPixmap("Assets/Icons/blue.svg"))
        self.ui.type_combo.setItemIcon(5, QPixmap("Assets/Icons/white.svg"))
        self.ui.type_combo.setItemIcon(6, QPixmap("Assets/Icons/amber.svg"))
        self.ui.type_combo.setItemIcon(7, QPixmap("Assets/Icons/cyan.svg"))
        self.ui.type_combo.setItemIcon(8, QPixmap("Assets/Icons/magenta.svg"))
        self.ui.type_combo.setItemIcon(9, QPixmap("Assets/Icons/purple.svg"))
        self.ui.type_combo.setItemIcon(10, QPixmap("Assets/Icons/yellow.svg"))
        self.ui.type_combo.setItemIcon(11, QPixmap("Assets/Icons/pan.svg"))
        self.ui.type_combo.setItemIcon(12, QPixmap("Assets/Icons/tilt.svg"))
        self.ui.type_combo.setItemIcon(13, QPixmap("Assets/Icons/beam.svg"))
        self.ui.type_combo.setItemIcon(14, QPixmap("Assets/Icons/gobo.svg"))
        self.ui.type_combo.setItemIcon(15, QPixmap("Assets/Icons/strobe.svg"))
        self.ui.type_combo.setItemIcon(16, QPixmap("Assets/Icons/nothing.svg"))

        # Add buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def check_and_add_row(self, item):
        if item.row() == self.ui.channel_table.rowCount() - 1:
            self.ui.channel_table.insertRow(self.ui.channel_table.rowCount())

    def accept(self):
        # Check if the channel is named
        if not self.ui.name_edit.text():
            error_dialog = AcceptInfoDialog("The channel needs to be named.")
            error_dialog.exec()
            return

        error_dialog = AcceptInfoDialog("The channel will now be saved. If misconfigured there might be unexpected behaviour.", error_message=False)
        error_dialog.exec()

        # Construct channel data
        self.channel_data = {
            "name": self.ui.name_edit.text(),
            "type": self.ui.type_combo.currentText()
        }
        for section in range(self.ui.channel_table.rowCount()):
            if self.ui.channel_table.item(section, 0) and not self.ui.channel_table.item(section, 0).text() == "":
                self.channel_data[section] = {
                    "minimum": self.ui.channel_table.item(section, 0).text(),
                    "maximum": self.ui.channel_table.item(section, 1).text(),
                    "description": self.ui.channel_table.item(section, 2).text()
                }

        return super().accept()
