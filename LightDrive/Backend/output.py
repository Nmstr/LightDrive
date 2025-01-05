from PySide6.QtWidgets import QMessageBox
from .artnet import ArtnetOutput

class OutputSnippet:
    def __init__(self, dmx_output, values: dict) -> None:
        """
        Creates a snippet
        :param dmx_output: An instance of the DmxOutput class (used to tick the output after updating values)
        :param values: The values to set.
                       (E.g.:
                       1 universe - {universe_id: {channel: value, channel: value}} or
                       multiple universes - {universe_id: {channel: value, channel: value}, universe_id: {channel: value}}
                       )
        """
        self.dmx_output = dmx_output
        self.values = values

    def update_values(self, values: dict) -> None:
        """
        Updates the values of the snippet
        :param values: The values to update
        :return: None
        """
        self.values = values
        self.dmx_output.tick_output()

class DmxUniverse:
    def __init__(self, universe_uuid: str = None, universe_name: str = None, configuration: dict = None) -> None:
        """
        Creates a universe
        :param universe_uuid: The uuid of the universe
        :param universe_name: The name of the universe
        :param configuration: Full universe configuration (this is used to load a workspace; this disregards the name and uuid parameters)
        """
        self.configuration = configuration
        if not self.configuration:
            self.configuration = {
                "uuid": universe_uuid,
                "name": universe_name,
                "ArtNet": {
                    "active": False,
                    "target_ip": "",
                    "universe": 0,
                    "hz": 0
                }
            }
        self.artnet = None

    def configure_artnet(self, active: bool, target_ip: str, artnet_universe: int, hz: int) -> None:
        """
        Configures the ArtNet backend
        :param active: Whether the backend should be active
        :param target_ip: The target IP address
        :param artnet_universe: The ArtNet universe to use
        :param hz: The refresh rate
        :return: None
        """
        self.configuration["ArtNet"]["active"] = active
        self.configuration["ArtNet"]["target_ip"] = target_ip
        self.configuration["ArtNet"]["universe"] = artnet_universe
        self.configuration["ArtNet"]["hz"] = hz
        if active:
            self.artnet = ArtnetOutput(target_ip, artnet_universe, hz)
        else:
            self.artnet = None

    def stop(self) -> None:
        """
        Gracefully stops the backend
        :return: None
        """
        if self.artnet:
            self.artnet.stop()

class DmxOutput:
    def __init__(self, window) -> None:
        """
        Creates the output class to output data
        :param window: The main window
        """
        self.window = window
        self.universes = {}
        self.universe_configuration = {}
        self.active_snippets = []

    def set_single_value(self, universe: int, channel: int, value: int) -> None:
        """
        Sets a single channel to another value (this is kept for the console tab; console tab needs to be overhauled)
        :param universe: The universe to output to
        :param channel: The channel to set
        :param value: The value that should be set
        :return: None
        """
        if channel < 1 or channel > 512:
            print("ERROR: Channel out of range.")
            return
        universe = self.universes.get(universe)
        if universe is None:
            return
        for backend in universe:
            backend.set_single_value(channel, value)

    def insert_snippet(self, snippet: OutputSnippet) -> None:
        """
        Inserts a snippet into the output
        :param snippet: The snippet to insert
        :return: None
        """
        self.active_snippets.append(snippet)
        self.tick_output()

    def remove_snippet(self, snippet: OutputSnippet) -> None:
        """
        Removes a snippet from the output
        :param snippet: The snippet to remove
        :return: None
        """
        self.active_snippets.remove(snippet)
        self.tick_output()

    def tick_output(self) -> None:
        """
        Ticks the output updating values in the backends
        :return: None
        """
        for universe in self.universes:
            universe_values = [0] * 512
            for snippet in self.active_snippets:
                for snippet_universe in snippet.values:
                    if snippet_universe == universe:
                        for channel in snippet.values[universe]:
                            universe_values[channel - 1] = snippet.values[universe][channel]
            for backend in self.universes[universe]:
                backend.set_multiple_values(universe_values)

    def create_universe(self, universe_uuid: str, universe_name: str) -> None:
        """
        Adds a universe to the output
        :param universe_uuid: The uuid of the universe
        :param universe_name: The name of the universe
        :return: None
        """
        self.universes[universe_uuid] = DmxUniverse(universe_uuid, universe_name)

    def configure_artnet(self, universe_uuid: str, active: bool, target_ip: str, artnet_universe: int, hz: int) -> None:
        """
        Configures the ArtNet backend for a universe
        :param universe_uuid: The uuid of the universe to configure
        :param active: Whether the backend should be active
        :param target_ip: The target IP address
        :param artnet_universe: The ArtNet universe to use
        :param hz: The refresh rate
        :return: None
        """
        universe = self.universes.get(universe_uuid)
        if universe is None:
            return
        universe.configure_artnet(active, target_ip, artnet_universe, hz)

    def write_output_configuration(self, configuration: dict) -> None:
        """
        Writes a whole configuration at once. This is used to load a configuration when opening a workspace.
        :param configuration: The configuration to write
        :return: None
        """
        for universe_uuid, universe_data in configuration.items():
            self.create_universe(universe_uuid, universe_data["name"])
            self.configure_artnet(universe_uuid,
                                  universe_data["ArtNet"]["active"],
                                  universe_data["ArtNet"]["target_ip"],
                                  universe_data["ArtNet"]["universe"],
                                  universe_data["ArtNet"]["hz"])
            self.window.io_add_universe_entry(universe_uuid, universe_data["name"])

    def get_universe_data(self, universe_uuid: str) -> dict:
        """
        Gets the data about a specific universe
        :param universe_uuid: The uuid of the universe to get the data from
        :return: The data about the universe
        """

    def get_configuration(self) -> dict:
        """
        Gets the configuration of the output (used to save the workspace)
        :return: The configuration of the output
        """
        universe_configuration = {}
        for universe in self.universes:
            universe_configuration[universe] = self.universes[universe].configuration
        return universe_configuration

    def shutdown_output(self) -> None:
        """
        Gracefully stops all backends
        :return: None
        """
        print(self.universes)
        for universe in self.universes:
            self.universes[universe].stop()
