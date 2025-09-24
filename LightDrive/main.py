from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import sys

def main() -> None:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load("main.qml")

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
