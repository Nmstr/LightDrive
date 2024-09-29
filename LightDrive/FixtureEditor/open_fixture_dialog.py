from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton
import os

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
            fixture_btn = QPushButton(fixture.split(".")[0], self)
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
