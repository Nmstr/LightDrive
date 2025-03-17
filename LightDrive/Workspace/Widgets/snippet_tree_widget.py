from PySide6.QtWidgets import QTreeWidget
from PySide6.QtCore import Qt

class SnippetTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = parent
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

    def dropEvent(self, event):  # noqa: N802
        target_item = self.itemAt(event.pos())
        if target_item and target_item.data(0, Qt.UserRole) == "directory":
            super().dropEvent(event)
            dragged_item = event.source().selectedItems()[0]
            self.window.snippet_manager.directory_manager.dir_add_snippet(target_item.uuid, dragged_item.uuid)
        else:
            event.ignore()
