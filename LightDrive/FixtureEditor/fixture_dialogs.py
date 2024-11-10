from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton
import json
import os

class SaveErrorDialog(QDialog):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.setWindowTitle("Error Saving Fixture")
        self.setFixedSize(500, 100)

        qbtn = (
            QDialogButtonBox.Ok
        )

        self.buttonBox = QDialogButtonBox(qbtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        self.label = QLabel(message, self)
        layout.addWidget(self.label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

class OpenFixtureDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Open Fixture")
        self.clicked_fixture = None

        qbtn = (
            QDialogButtonBox.Cancel
        )

        self.buttonBox = QDialogButtonBox(qbtn)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        self.label = QLabel("Which fixture do you want to open?", self)
        layout.addWidget(self.label)

        fixture_dir = os.getenv('XDG_CONFIG_HOME', default=os.path.expanduser('~/.config')) + '/LightDrive/fixtures/'
        for fixture in os.listdir(fixture_dir):
            with open(os.path.join(fixture_dir, fixture)) as f:
                fixture_data = json.load(f)
            fixture_btn = QPushButton(fixture_data["name"], self)
            fixture_btn.clicked.connect(lambda _, f=fixture: self.exit(f))
            layout.addWidget(fixture_btn)

        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def exit(self, fixture) -> None:
        """
        Set a value and exit the dialog
        :return: None
        """
        self.clicked_fixture = fixture
        self.accept()

class FixtureInfoDialog(QDialog):
    def __init__(self, message: str, *, width: int = 500) -> None:
        super().__init__()
        self.setWindowTitle("Info")
        self.setFixedSize(width, 100)

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
