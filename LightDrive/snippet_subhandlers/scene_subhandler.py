from data_structures import SceneSnippet, SceneChannelEntry
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import QObject, Slot, Qt, QByteArray, QAbstractListModel, QModelIndex

class ChannelModel(QAbstractListModel):
    ValueRole = Qt.UserRole + 1
    ActiveRole = Qt.UserRole + 2

    def __init__(self, channels=None, parent=None):
        super().__init__(parent)
        self._channels = channels or []

    def rowCount(self, parent=QModelIndex()):  # noqa: N802
        return len(self._channels)

    def data(self, index, role):
        if not index.isValid():
            return None
        channel = self._channels[index.row()]
        if role == self.ValueRole:
            return channel["value"]
        elif role == self.ActiveRole:
            return channel["active"]
        return None

    def roleNames(self):  # noqa: N802
        return {
            self.ValueRole: b"value",
            self.ActiveRole: b"active",
        }

class SceneSubhandler(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root

    @Slot()
    def add(self):
        self.root.workspace.snippets.append(SceneSnippet("Scene"))
        self.root.data_models.build_snippet_model()

    def load(self, snippet: SceneSnippet) -> None:
        if not snippet:
            return

        scene_model = QStandardItemModel()
        scene_model.setItemRoleNames({
            Qt.DisplayRole: QByteArray(b"display"),
            Qt.UserRole: QByteArray(b"uuid"),
            Qt.UserRole + 3: QByteArray(b"channelsModel"),
        })

        for fixture_uuid, channels in snippet.channel_values.items():
            # Get fixture
            for fixture in self.root.workspace.fixtures:
                if fixture.uuid == fixture_uuid:
                    fixture = fixture
                    break
            else:
                return

            fixture_item = QStandardItem(fixture.name)
            fixture_item.setData(fixture.uuid, Qt.UserRole)
            channels_data = [{"value": channel.value, "active": channel.active} for channel in channels]
            fixture_item.setData(ChannelModel(channels_data, parent=self.root.engine), Qt.UserRole + 3)

            scene_model.appendRow(fixture_item)

        self.root.snippet_handler.loadScene.emit(snippet.uuid, snippet.name, scene_model)

    @Slot(str, str)
    def add_fixture(self, snippet_uuid: str, fixture_uuid: str) -> None:
        for snippet in self.root.workspace.snippets:  # Get snippet
            if snippet.uuid == snippet_uuid:
                snippet = snippet
                break
        else:
            return
        for fixture in self.root.workspace.fixtures:  # Get fixture
            if fixture.uuid == fixture_uuid:
                fixture = fixture
                break
        else:
            return

        for fixture_uuid, _ in snippet.channel_values.items():
            if fixture_uuid == fixture.uuid:
                return  # Fixture already added

        # Add fixture to scene
        snippet.channel_values[fixture.uuid] = []
        for channel in fixture.channels:
            snippet.channel_values[fixture.uuid].append(SceneChannelEntry())

    @Slot(str, str, int, bool)
    def set_active(self, scene_uuid: str, fixture_uuid: str, channel: int, active: bool) -> None:
        for snippet in self.root.workspace.snippets:  # Find scene
            if snippet.uuid == scene_uuid:
                scene = snippet
                break
        else:
            return

        channels = scene.channel_values.get(fixture_uuid, None)
        if not channels:
            return
        channel_data = channels[channel] if len(channels) > channel else None
        if not channel_data:
            return

        channel_data.active = active
