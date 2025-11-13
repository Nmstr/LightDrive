import resource_rc  # noqa: F401
from data_structures import Workspace
from data_models import DataModels
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
        self.universe_handler = UniverseHandler(self)
        engine.rootContext().setContextProperty("universeHandler", self.universe_handler)

        # Models
        self.data_models = DataModels()
        fixtures_model = self.data_models.build_fixtures_model()
        engine.rootContext().setContextProperty("fixturesModel", fixtures_model)
        snippet_model = self.data_models.build_snippet_model()
        engine.rootContext().setContextProperty("snippetModel", snippet_model)
        universe_list_model = self.data_models.build_universe_list_model()
        engine.rootContext().setContextProperty("universeListModel", universe_list_model)

        engine.addImportPath(QDir.currentPath() + "/qml")
        engine.load("qml/main.qml")

        if not engine.rootObjects():
            sys.exit(-1)
        sys.exit(app.exec())

if __name__ == "__main__":
    LightDrive()

