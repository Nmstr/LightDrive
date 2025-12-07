from data_structures import SceneSnippet
from output.output_snippets.generic_output_snippet import GenericOutputSnippet

class SceneOutputSnippet(GenericOutputSnippet):
    def __init__(self, root, scene_data: SceneSnippet) -> None:
        self.scene_data = scene_data
        super().__init__(root)

    def get_values(self) -> dict[int, int]:
        values = {}
        for fixture_uuid, channels in self.scene_data.channel_values.items():
            fixture = self._get_fixture(fixture_uuid)
            for i, channel in enumerate(channels):
                if channel.active:
                    values[i + fixture.address] = channel.value

        return values
