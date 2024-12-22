from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QDialog, \
    QVBoxLayout, QGraphicsItemGroup, QGraphicsTextItem
from PySide6.QtGui import QPen
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt

class DeskButtonConfig(QDialog):
    def __init__(self, button_data) -> None:
        """
        Create a dialog for configuring a button
        :param button_data: The data for the button (created if not provided)
        """
        super().__init__()
        self.setWindowTitle("LightDrive - Button Properties")

        # Load the UI file
        loader = QUiLoader()
        ui_file = QFile("Workspace/Dialogs/desk_button_config.ui")
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setGeometry(self.ui.geometry())

        # Add buttons
        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.reject)

        self.ui.label_edit.setText(button_data["label"])

        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

class DeskButton(QGraphicsItemGroup):
    def __init__(self, desk, x, y, width, height, button_data = None) -> None:
        """
        Create a button object
        :param button_data: The data for the button (created if not provided)
        """
        super().__init__()
        if not button_data:
            self.button_data = {
                "label": "Button",
            }
        self.desk = desk
        self.pressed = False
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.body = QGraphicsRectItem(x, y, width, height)
        self.body.setBrush(Qt.lightGray)
        self.addToGroup(self.body)
        self.label = QGraphicsTextItem(self.button_data["label"])
        self.label.setDefaultTextColor(Qt.black)
        self.addToGroup(self.label)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """
        Activate or deactivate the button
        """
        if not self.desk.window.live_mode:
            return  # Disallow button press outside live mode

        self.pressed = not self.pressed
        if self.pressed:
            self.body.setBrush(Qt.darkGray)
            self.body.setPen(QPen(Qt.green, 2))
        else:
            self.body.setBrush(Qt.lightGray)
            self.body.setPen(QPen(Qt.black, 1))
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """
        Edit the button's properties
        """
        if self.desk.window.live_mode:
            return  # Disable editing in live mode
        config_dlg = DeskButtonConfig(button_data=self.button_data)
        if config_dlg.exec():
            self.button_data["label"] = config_dlg.ui.label_edit.text()
            self.label.setPlainText(config_dlg.ui.label_edit.text())
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        """
        Move the button
        """
        if self.desk.window.live_mode:
            return  # Disable movement in live mode
        super().mouseMoveEvent(event)

class ControlDesk(QGraphicsView):
    def __init__(self, window: QMainWindow) -> None:
        """
        Create the control desk object
        :param window: The main window
        """
        super().__init__(window)
        self.window = window
        self.scene = QGraphicsScene(window)
        self.setScene(self.scene)

    def add_btn(self) -> None:
        """
        Add a button to the control desk
        """
        button = DeskButton(self, 0, 0, 100, 100)
        self.scene.addItem(button)

    def add_fader(self) -> None:
        """
        Add a slider to the control desk
        """
        pass

    def add_knob(self) -> None:
        """
        Add a knob to the control desk
        """
        pass

    def add_sound_trigger(self) -> None:
        """
        Add a sound trigger to the control desk
        """
        pass

    def add_label(self) -> None:
        """
        Add a label to the control desk
        """
        pass

    def add_clock(self) -> None:
        """
        Add a clock to the control desk
        """
        pass
