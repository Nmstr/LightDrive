import resource_rc  # noqa: F401
from PySide6.QtGui import QGuiApplication, QStandardItemModel, QStandardItem
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QDir
import sys

def build_fixtures_model() -> QStandardItemModel:
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["name"])
    for u in range(1, 4):
        universe_item = QStandardItem(f"Universe {u}")
        for f in range(1, 4):
            universe_item.appendRow(QStandardItem(f"Fixture {f}"))
        model.appendRow(universe_item)
    return model

def build_snippet_model() -> QStandardItemModel:
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Name"])
    for s in range(1, 7):
        snippet_item = QStandardItem(f"Snippet {s}")
        if s == 3:
            snippet_item.setText("Directory 1")
            for ss in range(1, 4):
                snippet_item.appendRow(QStandardItem(f"Snippet {ss}"))
        model.appendRow(snippet_item)
    return model

def main() -> None:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    fixtures_model = build_fixtures_model()
    engine.rootContext().setContextProperty('fixturesModel', fixtures_model)
    snippet_model = build_snippet_model()
    engine.rootContext().setContextProperty('snippetModel', snippet_model)

    engine.addImportPath(QDir.currentPath() + "/qml")
    engine.load("qml/main.qml")

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
