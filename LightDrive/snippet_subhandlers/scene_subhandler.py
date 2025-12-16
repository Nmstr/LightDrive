from data_structures import SceneSnippet, SceneChannelEntry
from output.output_snippets.scene_output_snippet import SceneOutputSnippet
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
    def __init__(self, root, parent):
        super().__init__(parent)
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

        for output_snippet_uuid in self.root.snippet_handler.output_snippets:
            if output_snippet_uuid == snippet.uuid:
                showing = True
                break
        else:
            showing = False

        self.root.snippet_handler.loadScene.emit(snippet.uuid, snippet.name, showing, scene_model)

    @Slot(str)
    def output_scene(self, scene_uuid: str) -> None:
        for snippet in self.root.workspace.snippets:
            if snippet.uuid == scene_uuid:
                scene = snippet
                break
        else:
            return

        output_snippet = SceneOutputSnippet(self.root, 0, scene)
        self.root.snippet_handler.output_snippets[scene_uuid] = output_snippet
        self.root.output_manager.add_snippet(output_snippet)

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

    def _get_channel_entry(self, scene_uuid: str, fixture_uuid: str, channel: str) -> SceneChannelEntry | None:
        for snippet in self.root.workspace.snippets:  # Find scene
            if snippet.uuid == scene_uuid:
                scene = snippet
                break
        else:
            return

        channels = scene.channel_values.get(fixture_uuid, None)
        if not channels:
            return
        channel_entry = channels[channel] if len(channels) > channel else None
        return channel_entry

    @Slot(str, str, int, bool)
    def set_active(self, scene_uuid: str, fixture_uuid: str, channel: int, active: bool) -> None:
        channel_entry = self._get_channel_entry(scene_uuid, fixture_uuid, channel)
        channel_entry.active = active

    @Slot(str, str, int, int)
    def set_value(self, scene_uuid: str, fixture_uuid: str, channel: int, value: int) -> None:
        channel_entry = self._get_channel_entry(scene_uuid, fixture_uuid, channel)
        channel_entry.value = value
