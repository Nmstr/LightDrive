from PySide6.QtWidgets import QTreeWidget
from PySide6.QtCore import Qt

class SnippetTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

    def dropEvent(self, event):  # noqa: N802
        target_item = self.itemAt(event.pos())
        if target_item and target_item.data(0, Qt.UserRole) == "directory":
            super().dropEvent(event)
        else:
            event.ignore()
