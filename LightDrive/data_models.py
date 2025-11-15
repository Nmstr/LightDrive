from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QByteArray

class DataModels:
    def __init__(self, root):
        self.root = root
        self.fixtures_model = QStandardItemModel()
        self.build_fixtures_model()
        self.snippet_model = QStandardItemModel()
        self.build_snippet_model()
        self.universe_list_model = []
        self.build_universe_list_model()
        self.universe_model = QStandardItemModel()
        self.universe_model.setItemRoleNames({
            Qt.DisplayRole: QByteArray(b"display"),
            Qt.UserRole: QByteArray(b"uuid"),
        })
        self.build_universe_model()

    def build_all(self) -> None:
        self.build_fixtures_model()
        self.build_snippet_model()
        self.build_universe_list_model()
        self.build_universe_model()

    def build_fixtures_model(self) -> None:
        model = self.fixtures_model
        model.clear()

        model.setHorizontalHeaderLabels(["name"])
        for u in range(1, 4):
            universe_item = QStandardItem(f"Universe {u}")
            for f in range(1, 4):
                universe_item.appendRow(QStandardItem(f"Fixture {f}"))
            model.appendRow(universe_item)

    def build_snippet_model(self) -> None:
        model = self.snippet_model
        model.clear()

        model.setHorizontalHeaderLabels(["Name"])
        for s in range(1, 7):
            snippet_item = QStandardItem(f"Snippet {s}")
            if s == 3:
                snippet_item.setText("Directory 1")
                for ss in range(1, 4):
                    snippet_item.appendRow(QStandardItem(f"Snippet {ss}"))
            model.appendRow(snippet_item)

    def build_universe_list_model(self) -> None:
        model = self.universe_list_model  # Type: list[str]
        model.clear()

        for universe in self.root.workspace.universes:
            model.append(universe.name)

    def build_universe_model(self) -> None:
        model = self.universe_model
        model.clear()

        for universe in self.root.workspace.universes:
            item = QStandardItem(universe.name)
            item.setData(universe.uuid, Qt.UserRole)
            model.appendRow(item)
        model.layoutChanged.emit()
