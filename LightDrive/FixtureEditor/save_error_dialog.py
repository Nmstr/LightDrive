from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

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
