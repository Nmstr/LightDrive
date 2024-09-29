from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, \
    QGraphicsEllipseItem, QPushButton, QGraphicsItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
import sys

class Keyframe(QGraphicsEllipseItem):
    def __init__(self, main_window: object, x: float, y: float, diameter: int) -> None:
        """
        Create a keyframe
        :param main_window: The main window
        :param x: The x position of the keyframe
        :param y: The y position of the keyframe
        :param diameter: The diameter of the keyframe
        :return: None
        """
        self.main_window = main_window
        super().__init__(x - diameter / 2, y - diameter / 2, diameter, diameter)
        self.setBrush(Qt.blue)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def mousePressEvent(self, event):  # noqa: N802
        """
        Changes the page to the keyframe page on left-click
        :param event: The event
        """
        self.main_window.set_page("keyframe_configuration")
        return super().mousePressEvent(event)

class Timeline(QGraphicsView):
    def __init__(self, main_window: object) -> None:
        """
        Create the timeline object
        :param main_window: The main window
        """
        self.main_window = main_window
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.timelines = []
        self.create_timeline()

    def create_timeline(self) -> None:
        """
        Create a timeline
        :return: None
        """
        y_position = len(self.timelines) * 60
        timeline_rect = QGraphicsRectItem(0, y_position, 800, 50)
        colors = [Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta, Qt.yellow, Qt.darkRed, Qt.darkGreen, Qt.darkBlue, Qt.darkCyan, Qt.darkMagenta, Qt.darkYellow]
        timeline_rect.setBrush(colors[len(self.timelines) % len(colors)])
        timeline_rect.setOpacity(0.25)
        self.scene.addItem(timeline_rect)
        self.timelines.append(timeline_rect)
        self.adjust_all_timeline_sizes(self.width(), 60)

    def add_keyframe(self, position) -> None:
        """
        Adds a keyframe onto a timeline
        :param position: The QPoint the object should be created at
        :return: None
        """
        for timeline in self.timelines:
            if timeline.rect().contains(position.x(), position.y()):
                timeline_y_center = timeline.rect().center().y()
                keyframe = Keyframe(self.main_window, position.x(), timeline_y_center, 10)
                self.scene.addItem(keyframe)
                break

    def adjust_all_timeline_sizes(self, width: int, height: int) -> None:
        """
        Adjusts the sizes of all the timelines
        :param width: The new width
        :param height: The new height
        :return: None
        """
        for timeline in self.timelines:
            timeline.setRect(0, timeline.rect().y(), width, height)

    def mousePressEvent(self, event):  # noqa: N802
        """
        Adds a keyframe on right-click
        :param event: The event
        """
        if event.button() == Qt.RightButton:
            # Add a new keyframe
            position = self.mapToScene(event.pos())
            self.add_keyframe(position)
        return super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):  # noqa: N802
        """
        Change the page to the timeline configuration page on double click
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton:
            self.main_window.set_page("timeline_configuration")
        return super().mouseDoubleClickEvent(event)

class TimelineEditor(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("LightDrive")

        # Load the stylesheet
        with open('style.qss', 'r') as f:
            app.setStyleSheet(f.read())

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("TimelineEditor/timeline_editor.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())
        self.showMaximized()

        self.timeline = Timeline(self)

        # Add a button to add a new timeline
        self.add_timeline_button = QPushButton("Add Timeline")
        self.add_timeline_button.clicked.connect(self.timeline.create_timeline)

        # Add timeline and button to layout
        layout = self.ui.timeline.layout()
        layout.addWidget(self.timeline)
        layout.addWidget(self.add_timeline_button)

        # Make the timeline the correct size initially
        self.timeline.adjust_all_timeline_sizes(self.width(), 60)

    def set_page(self, page: str) -> None:
        """
        Changes the page in the top display
        :param page: Str to identify the page
        :return: None
        """
        if page == "timeline_configuration":
            self.ui.top_display.setCurrentWidget(self.ui.timeline_configuration)
        elif page == "keyframe_configuration":
            self.ui.top_display.setCurrentWidget(self.ui.keyframe_configuration)

    def resizeEvent(self, event):  # noqa: N802
        """
        Changes the timeline sizes when the window is resized
        :param event: The event
        """
        try:
            self.timeline.adjust_all_timeline_sizes(self.width(), 60)
        except AttributeError:
            pass
        return super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimelineEditor()
    window.show()
    sys.exit(app.exec())
