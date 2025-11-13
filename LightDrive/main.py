import resource_rc  # noqa: F401
from data_structures import Workspace
from data_models import build_fixtures_model, build_snippet_model, build_universe_list_model
from universe_handler import UniverseHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QDir
import sys

def main() -> None:
    workspace = Workspace()

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Handlers
    universe_handler = UniverseHandler(workspace)
    engine.rootContext().setContextProperty("universeHandler", universe_handler)

    # Models
    fixtures_model = build_fixtures_model()
    engine.rootContext().setContextProperty("fixturesModel", fixtures_model)
    snippet_model = build_snippet_model()
    engine.rootContext().setContextProperty("snippetModel", snippet_model)
    universe_list_model = build_universe_list_model()
    engine.rootContext().setContextProperty("universeListModel", universe_list_model)

    engine.addImportPath(QDir.currentPath() + "/qml")
    engine.load("qml/main.qml")

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
