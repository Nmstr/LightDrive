from data_structures import SceneSnippet, SceneChannelEntry
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import QObject, Slot

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

        channel_model = QStandardItemModel()
        for fixture_uuid, channels in snippet.channel_values.items():
            # Get fixture
            for fixture in self.root.workspace.fixtures:
                if fixture.uuid == fixture_uuid:
                    fixture = fixture
                    break
            else:
                return

            fixture_item = QStandardItem(fixture.name)
            channel_model.appendRow(fixture_item)

        self.root.snippet_handler.loadScene.emit(snippet.uuid, snippet.name, channel_model)

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
