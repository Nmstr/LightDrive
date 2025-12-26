from data_structures import IoDeskItem, DeskItemConnector, DeskWire, DeskWireStop
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QObject, Slot

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

    def update(self) -> None:
        self.beginResetModel()
        self.items = self._root.workspace.desk_items
        self.endResetModel()

class ConnectorModel(QAbstractListModel):
    UuidRole = Qt.UserRole
    DataTypeRole = Qt.UserRole + 1

    def __init__(self, parent=None, root=None, item_uuid: str = None, side: str = None):
        super().__init__(parent)
        self.root = root
        self.item_uuid = item_uuid
        self.side = side
        self.connectors = self.build_connectors_list()

    def build_connectors_list(self) -> list:
        for item in self.root.workspace.desk_items:
            if item.uuid == self.item_uuid:
                desk_item = item
                break
        else:
            return []

        if not isinstance(desk_item, IoDeskItem):
            return []  # Not a desk item with connectors

        connectors = []
        if self.side == "input":
            for connector in desk_item.input_connectors:
                connectors.append(connector)
        elif self.side == "output":
            for connector in desk_item.output_connectors:
                connectors.append(connector)
        return connectors

    def rowCount(self, parent=QModelIndex()):  # noqa: N802
        return len(self.connectors)

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None

        connector = self.connectors[index.row()]
        if role == self.UuidRole:
            return connector.uuid
        elif role == self.DataTypeRole:
            return connector.data_type
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.UuidRole: b"uuid",
            self.DataTypeRole: b"data_type",
        }

class DeskHandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

        self.desk_content_model = DeskContentModel(self, self.root)

    @Slot(str, str, result="QVariant")
    def get_connector_model(self, item_uuid: str, side: str) -> ConnectorModel:
        model = ConnectorModel(self, self.root, item_uuid, side)
        return model

    def _find_connector_by_uuid(self, connector_uuid: str) -> DeskItemConnector | None:
        for item in self.root.workspace.desk_items:
            if isinstance(item, IoDeskItem):
                all_connectors = item.input_connectors + item.output_connectors
                for connector in all_connectors:
                    if connector.uuid == connector_uuid:
                        return connector
        return None

    def _get_item_of_connector(self, connector_uuid: str) -> IoDeskItem | None:
        """
        Returns the IoDeskItem that has a specific connector.
        :param connector_uuid: The uuid of the connector.
        :return: The IoDeskItem that has a specific connector (or None if it could not be found).
        """
        for item in self.root.workspace.desk_items:
            if isinstance(item, IoDeskItem):
                all_connectors = item.input_connectors + item.output_connectors
                for connector in all_connectors:
                    if connector.uuid == connector_uuid:
                        return item
        return None

    @Slot(str, str)
    def create_wire(self, output_connector_uuid, input_connector_uuid) -> None:
        # Get connectors
        starting_connector = self._find_connector_by_uuid(output_connector_uuid)
        ending_connector = self._find_connector_by_uuid(input_connector_uuid)
        if not starting_connector or not ending_connector:
            return  # Either connector not found

        # Get items
        starting_item = self._get_item_of_connector(starting_connector.uuid)
        ending_item = self._get_item_of_connector(ending_connector.uuid)

        # Calculate default positions for control points
        cp1x = starting_item.x + 50  # Slightly to the right of the item
        cp1y = starting_item.y
        cp2x = ending_item.x - 50  # Slightly to the left of the item
        cp2y = ending_item.y

        # Create wire
        self.root.workspace.desk_items.append(
            DeskWire(
                starting_connector_uuid=output_connector_uuid,
                ending_connector_uuid=input_connector_uuid,
                stops=[DeskWireStop(ending_item.x, ending_item.y, cp1x, cp1y, cp2x, cp2y)]
            )
        )

        # Update model
        self.desk_content_model.update()
