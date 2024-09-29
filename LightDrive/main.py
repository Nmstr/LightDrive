from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, \
    QGraphicsEllipseItem, QPushButton, QGraphicsItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QBrush
import sys

class Keyframe(QGraphicsEllipseItem):
    def __init__(self, x, y, diameter):
        super().__init__(x - diameter / 2, y - diameter / 2, diameter, diameter)
        self.setBrush(Qt.blue)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

class Timeline(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.timelines = []
        self.create_timeline()

    def create_timeline(self):
        y_position = len(self.timelines) * 60
        timeline_rect = QGraphicsRectItem(0, y_position, 800, 50)
        colors = [Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta, Qt.yellow, Qt.darkRed, Qt.darkGreen, Qt.darkBlue, Qt.darkCyan, Qt.darkMagenta, Qt.darkYellow]
        timeline_rect.setBrush(colors[len(self.timelines) % len(colors)])
        timeline_rect.setOpacity(0.25)
        self.scene.addItem(timeline_rect)
        self.timelines.append(timeline_rect)
        self.adjust_all_timeline_sizes(self.width(), 60)

    def add_keyframe(self, position):
        for timeline in self.timelines:
            if timeline.rect().contains(position.x(), position.y()):
                timeline_y_center = timeline.rect().center().y()
                keyframe = Keyframe(position.x(), timeline_y_center, 10)
                self.scene.addItem(keyframe)
                break

    def adjust_all_timeline_sizes(self, width, height):
        for timeline in self.timelines:
            timeline.setRect(0, timeline.rect().y(), width, height)

    def change_timeline_color(self, index, color):
        if 0 <= index < len(self.timelines):
            timeline = self.timelines[index]
            timeline.setBrush(QBrush(color))

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.RightButton:
            # Add a new keyframe
            position = self.mapToScene(event.pos())
            self.add_keyframe(position)
        return super().mousePressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("LightDrive")

        # Load the stylesheet
        with open('style.qss', 'r') as f:
            app.setStyleSheet(f.read())

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("main.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())
        self.showMaximized()

        self.timeline = Timeline()

        # Add a button to add a new timeline
        self.add_timeline_button = QPushButton("Add Timeline")
        self.add_timeline_button.clicked.connect(self.add_timeline)

        # Add timeline and button to layout
        layout = self.ui.timeline.layout()
        layout.addWidget(self.timeline)
        layout.addWidget(self.add_timeline_button)

        # Make the timeline the correct size initially
        self.timeline.adjust_all_timeline_sizes(self.width(), 60)

    def add_timeline(self):
        self.timeline.create_timeline()

    def resizeEvent(self, event):  # noqa: N802
        try:
            self.timeline.adjust_all_timeline_sizes(self.width(), 60)
        except AttributeError:
            pass
        return super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
