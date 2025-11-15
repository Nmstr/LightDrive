import resource_rc  # noqa: F401
from data_structures import Workspace
from data_models import DataModels
from workspace_handler import WorkspaceHandler
from universe_handler import UniverseHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QDir
import sys

class LightDrive:
    def __init__(self):
        self.workspace = Workspace()

        app = QGuiApplication(sys.argv)
        engine = QQmlApplicationEngine()

        # Handlers
        self.workspace_handler = WorkspaceHandler(self)
        engine.rootContext().setContextProperty("workspaceHandler", self.workspace_handler)
        self.universe_handler = UniverseHandler(self)
        engine.rootContext().setContextProperty("universeHandler", self.universe_handler)

        # Models
        self.data_models = DataModels(self)
        engine.rootContext().setContextProperty("fixturesModel", self.data_models.fixtures_model)
        engine.rootContext().setContextProperty("snippetModel", self.data_models.snippet_model)
        engine.rootContext().setContextProperty("universeListModel", self.data_models.universe_list_model)
        engine.rootContext().setContextProperty("universeModel", self.data_models.universe_model)

        engine.addImportPath(QDir.currentPath() + "/qml")
        engine.load("qml/main.qml")

        if not engine.rootObjects():
            sys.exit(-1)
        sys.exit(app.exec())

if __name__ == "__main__":
    LightDrive()

