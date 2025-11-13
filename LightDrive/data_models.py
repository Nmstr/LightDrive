from PySide6.QtGui import QStandardItemModel, QStandardItem

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

def build_universe_list_model() -> list[str]:
    model = []
    for u in range(1, 4):
        model.append(f"Universe {u}")
    return model
