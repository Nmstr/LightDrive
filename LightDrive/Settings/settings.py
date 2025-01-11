from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QStyleFactory
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import configparser
import os

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LightDrive - Settings")
        self.settings_file = os.getenv("XDG_CONFIG_HOME", default=os.path.expanduser("~/.config")) + "/LightDrive/settings.ini"
        if not os.path.exists(self.settings_file):
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        self.config = configparser.ConfigParser()
        self.config.read(self.settings_file)

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Settings/settings.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        # Add buttons
        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)
        self.ui.button_box.clicked.connect(self.button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

        self.load_themes()

    def accept(self):
        self.save_settings()
        super().accept()

    def button_clicked(self, button):
        if self.ui.button_box.buttonRole(button) == QDialogButtonBox.ApplyRole:
            self.save_settings()

    def load_themes(self):
        available_themes = QStyleFactory.keys()
        for theme in available_themes:
            self.ui.theme_combo.addItem(theme)
        theme = self.config.get("Settings", "theme", fallback="Breeze")
        self.ui.theme_combo.setCurrentText(theme)

    def save_settings(self):
        theme = self.ui.theme_combo.currentText()
        self.config["Settings"] = {"theme": theme}
        with open(self.settings_file, "w") as configfile:
            self.config.write(configfile)
