import resource_rc  # noqa: F401
from data_structures import Workspace
from data_models import DataModels
from workspace_handler import WorkspaceHandler
from universe_handler import UniverseHandler
from fixture_handler import FixtureHandler
from snippet_handler import SnippetHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QDir
import argparse
import sys

class LightDrive:
    def __init__(self, default_workspace: str):
        self.workspace = Workspace()

        app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()

        # Handlers
        self.workspace_handler = WorkspaceHandler(self)
        self.engine.rootContext().setContextProperty("workspaceHandler", self.workspace_handler)
        self.universe_handler = UniverseHandler(self)
        self.engine.rootContext().setContextProperty("universeHandler", self.universe_handler)
        self.fixture_handler = FixtureHandler(self)
        self.engine.rootContext().setContextProperty("fixtureHandler", self.fixture_handler)
        self.snippet_handler = SnippetHandler(self)
        self.engine.rootContext().setContextProperty("snippetHandler", self.snippet_handler)

        # Models
        self.data_models = DataModels(self)
        self.engine.rootContext().setContextProperty("fixturesModel", self.data_models.fixtures_model)
        self.engine.rootContext().setContextProperty("snippetModel", self.data_models.snippet_model)
        self.engine.rootContext().setContextProperty("universeListModel", self.data_models.universe_list_model)
        self.engine.rootContext().setContextProperty("universeModel", self.data_models.universe_model)
        self.engine.rootContext().setContextProperty("fixtureBlueprintModel", self.data_models.fixture_blueprint_model)

        self.engine.addImportPath(QDir.currentPath() + "/qml")
        self.engine.load("qml/main.qml")

        if default_workspace:
            self.workspace_handler.open(default_workspace)

        if not self.engine.rootObjects():
            sys.exit(-1)
        sys.exit(app.exec())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LightDrive")
    parser.add_argument("-w", "--workspace", help="Open a workspace on launch")
    args = parser.parse_args()

    LightDrive(args.workspace)
