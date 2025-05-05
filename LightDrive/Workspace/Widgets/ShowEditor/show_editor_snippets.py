from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItemGroup, QGraphicsTextItem, QGraphicsItem, QMenu, \
    QInputDialog, QApplication
from PySide6.QtCore import Qt, QTimer

class SnippetTrack(QGraphicsRectItem):
    def __init__(self, show_editor) -> None:
        super().__init__()
        self.show_editor = show_editor

        # Create the track
        self.setRect(0, 0, self.show_editor.track_length, 100)
        self.setBrush(Qt.lightGray)
        self.setOpacity(0.3)

    def update_width(self) -> None:
        self.setRect(0, 0, self.show_editor.track_length * self.show_editor.zoom, 100)

class SnippetItem(QGraphicsItemGroup):
    def __init__(self, show_editor, snippet_item_uuid: str, snippet_uuid: str, length: int = 250, frame: int = 0, track: int = 0) -> None:
        super().__init__()
        self.uuid = snippet_item_uuid
        self.show_editor = show_editor
        self.snippet_uuid = snippet_uuid
        self.length = length
        self.frame = frame
        self.track = track
        self._disable_frame_updates = False

        width = self.show_editor.virtual_frame_from_x_pos(self.length)
        self.body = QGraphicsRectItem(0, 0, width, 100)
        self.body.setBrush(Qt.green)
        self.body.setOpacity(0.25)
        self.addToGroup(self.body)

        snippet_name = self.show_editor.window.snippet_manager.available_snippets[snippet_uuid].name
        self.label = QGraphicsTextItem(snippet_name)
        self.label.setPos(0, 0)
        self.addToGroup(self.label)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        x_pos = self.show_editor.x_pos_from_virtual_frame(self.frame)
        y_pos = self.track * 100 + 50
        self.setPos(x_pos, y_pos)

        self.context_menu = QMenu()
        change_length_action = self.context_menu.addAction("Change Length")
        change_length_action.triggered.connect(self.change_length)
        remove_action = self.context_menu.addAction("Remove")
        remove_action.triggered.connect(self.remove_snippet_item)

    def contextMenuEvent(self, event) -> None:  # noqa: N802
        """
        Show the context menu
        :param event: The context menu event
        """
        self.context_menu.exec(event.screenPos())

    def change_length(self, new_length: int = None) -> None:
        """
        Change the length of the snippet
        :param new_length: The new length of the snippet
        :return: None
        """
        if not new_length:
            dlg = QInputDialog()
            dlg.setInputMode(QInputDialog.IntInput)
            dlg.setIntMinimum(1)
            dlg.setIntMaximum(32767)
            dlg.setIntValue(self.length)
            if not dlg.exec():
                return
            new_length = dlg.intValue()
        self.length = new_length
        self.update_width_position()
        self.show_editor.show_snippet.added_snippets[self.uuid]["length"] = new_length

    def remove_snippet_item(self) -> None:
        """
        Removes the snippet from the show
        :return: None
        """
        self.show_editor.remove_snippet_item(self.uuid)

    def get_snap_position(self, current_x_pos: int) -> int:
        """
        Get the position the snippet should be snapped to (closest marker)
        :return: The snap position
        """
        if QApplication.instance().keyboardModifiers() == Qt.ShiftModifier:
            return current_x_pos  # No snapping if shift is pressed
        current_time = self.show_editor.x_pos_from_virtual_frame(current_x_pos) / 100
        close_markers = [self.show_editor.onset_markers.get_marker(current_time),
                         self.show_editor.beat_markers.get_marker(current_time),
                         self.show_editor.vary_beat_markers.get_marker(current_time)]
        valid_markers = [marker for marker in close_markers if marker is not None]
        if not valid_markers:
            return current_x_pos  # If no markers are found, return the current position
        closest_marker_time = min(valid_markers, key=lambda x: abs(x - current_time))
        marker_pos = self.show_editor.virtual_frame_from_x_pos(closest_marker_time * 100)
        return marker_pos

    def itemChange(self, change, value):  # noqa: N802
        if change == QGraphicsItem.ItemPositionChange:
            # Keep in the middle of the tracks
            track_number = round((value.y() - 50) / 100)
            value.setY(track_number * 100 + 50)
            if value.y() < 150: # Upper bounds
                value.setY(150)
            if value.x() < 0: # Left bounds
                value.setX(0)
            if not QApplication.instance().keyboardModifiers() == Qt.ShiftModifier:
                try:
                    snap_pos = self.get_snap_position(value.x())
                    self.show_editor.extended_marker.show()
                    self.show_editor.extended_marker.setX(snap_pos)
                    value.setX(snap_pos)
                except TypeError:
                    self.show_editor.extended_marker.hide()
                except AttributeError:
                    print("Marker not found")

            if not self._disable_frame_updates:
                self.frame = self.show_editor.x_pos_from_virtual_frame(value.x())
                if self.show_editor.show_snippet.added_snippets.get(self.uuid):
                    self.show_editor.show_snippet.added_snippets[self.uuid]["track"] = track_number
                    self.show_editor.show_snippet.added_snippets[self.uuid]["frame"] = self.frame

        return super().itemChange(change, value)

    def update_width_position(self) -> None:
        width = self.show_editor.virtual_frame_from_x_pos(self.length)
        self.body.setRect(0, 0, width, 100)

        x_pos = self.show_editor.virtual_frame_from_x_pos(self.frame)
        self._disable_frame_updates = True
        self.setX(x_pos)
        self.timer = QTimer()
        self.timer.setInterval(100)  # This feels hacky, but it works
        self.timer.timeout.connect(lambda: setattr(self, '_disable_frame_updates', False))
        self.timer.start()
