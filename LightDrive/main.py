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

def main() -> None:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    fixtures_model = build_fixtures_model()
    engine.rootContext().setContextProperty('fixturesModel', fixtures_model)

    engine.addImportPath(QDir.currentPath() + "/qml")
    engine.load("qml/main.qml")

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
