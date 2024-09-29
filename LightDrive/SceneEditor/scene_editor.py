from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys

class SceneEditor(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("SceneEditor")
        self.setWindowTitle("LightDrive - Scene Editor")
        self.file_path = None
        self.channels = []

        # Load the stylesheet
        with open('style.qss', 'r') as f:
            app.setStyleSheet(f.read())

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("SceneEditor/scene_editor.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SceneEditor()
    window.show()
    sys.exit(app.exec())
