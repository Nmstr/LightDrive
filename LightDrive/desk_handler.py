from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QObject

class DeskContentModel(QAbstractListModel):
    ItemTypeRole = Qt.UserRole
    # Generic roles
    UuidRole = Qt.UserRole + 1
    XRole = Qt.UserRole + 2
    YRole = Qt.UserRole + 3
    WidthRole = Qt.UserRole + 4
    HeightRole = Qt.UserRole + 5
    # Button roles
    HotkeyRole = Qt.UserRole + 6
    ModeRole = Qt.UserRole + 7
    FlashDurationRole = Qt.UserRole + 8
    # Fader roles
    DisplayStyleRole = Qt.UserRole + 9
    MinRole = Qt.UserRole + 10
    MaxRole = Qt.UserRole + 11
    StepSizeRole = Qt.UserRole + 12
    InvertedRole = Qt.UserRole + 13
    # Knob roles
    # All roles (display style, min, max and step size) already implemented in fader
    # Clock roles
    # ModeRole already implemented in button
    TimerDurationRole = Qt.UserRole + 14
    # Snippet Output roles
    SnippetUuidRole = Qt.UserRole + 15
    PriorityRole = Qt.UserRole + 16

    def __init__(self, parent=None, root=None):
        super().__init__(parent)
        self._root = root
        self.items = self._root.workspace.desk_items

    def rowCount(self, parent=QModelIndex()):  # noqa: N802
        return len(self.items)

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None

        item = self.items[index.row()]
        if role == Qt.DisplayRole:
            return item.name
        elif role == self.ItemTypeRole:
            return type(item).__name__  # Name of the class
        elif role == self.UuidRole:
            return item.uuid
        elif role == self.XRole:
            return item.x
        elif role == self.YRole:
            return item.y
        elif role == self.WidthRole:
            return item.width
        elif role == self.HeightRole:
            return item.height
        elif role == self.HotkeyRole:
            return item.hotkey
        elif role == self.ModeRole:
            return item.mode
        elif role == self.FlashDurationRole:
            return item.flashduration
        elif role == self.DisplayStyleRole:
            return item.displaystyle
        elif role == self.MinRole:
            return item.min
        elif role == self.MaxRole:
            return item.max
        elif role == self.StepSizeRole:
            return item.stepsize
        elif role == self.InvertedRole:
            return item.inverted
        elif role == self.TimerDurationRole:
            return item.timerduration
        elif role == self.SnippetUuidRole:
            return item.snippet_uuid
        elif role == self.PriorityRole:
            return item.priority
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.ItemTypeRole: b"itemType",
            self.UuidRole: b"uuid",
            self.XRole: b"x",
            self.YRole: b"y",
            self.WidthRole: b"width",
            self.HeightRole: b"height",
            self.HotkeyRole: b"hotkey",
            self.ModeRole: b"mode",
            self.FlashDurationRole: b"flashDuration",
            self.DisplayStyleRole: b"displayStyle",
            self.MinRole: b"min",
            self.MaxRole: b"max",
            self.StepSizeRole: b"stepSize",
            self.InvertedRole: b"inverted",
            self.TimerDurationRole: b"timerDuration",
            self.SnippetUuidRole: b"snippetUuid",
            self.PriorityRole: b"priority",
        }

class DeskHandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

        from data_structures import DeskButton, DeskFader, DeskKnob, DeskLabel, DeskClock, DeskSubdesk, DeskSnippetOutput
        self.root.workspace.desk_items.append(DeskButton("Button", x=100, y=100))
        self.root.workspace.desk_items.append(DeskFader("Fader", x=250, y=100))
        self.root.workspace.desk_items.append(DeskKnob("Knob", x=350, y=100))
        self.root.workspace.desk_items.append(DeskLabel("Label", x=100, y=50))
        self.root.workspace.desk_items.append(DeskClock("Clock", x=250, y=50))
        self.root.workspace.desk_items.append(DeskSubdesk("Subdesk", x=100, y=250))
        self.root.workspace.desk_items.append(DeskSnippetOutput("Snippet Output", x=400, y=250))

        self.desk_content_model = DeskContentModel(self, self.root)
