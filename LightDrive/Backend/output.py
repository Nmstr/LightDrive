from .artnet import ArtnetOutput
from .tcp_socket import TcpSocketOutput

class OutputSnippet:
    def __init__(self, dmx_output, values: dict) -> None:
        """
        Creates a snippet
        :param dmx_output: An instance of the DmxOutput class (used to tick the output after updating values)
        :param values: The values to set.
                       (E.g.:
                       1 universe - {universe_uuid: {channel: value, channel: value}} or
                       multiple universes - {universe_uuid: {channel: value, channel: value}, universe_uuid: {channel: value}}
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

class ConsoleOutputSnippet(OutputSnippet):
    def __init__(self, dmx_output) -> None:
        """
        Creates a custom snippet for the console output
        :param dmx_output: An instance of the DmxOutput class (used to tick the output after updating values)
        """
        super().__init__(dmx_output, {})

    def update_value(self, universe, channel, value) -> None:
        """
        Updates a single value of the snippet
        :param universe: The universe to update
        :param channel: The channel to update
        :param value: The value to set
        :return: None
        """
        if universe not in self.values:
            self.values[universe] = {}
        self.values[universe][channel] = value
        self.dmx_output.tick_output()

    def remove_value(self, universe, channel) -> None:
        """
        Removes a single value from the snippet
        :param universe: The universe to remove the value from
        :param channel: The channel to remove
        :return: None
        """
        if universe in self.values:
            if channel in self.values[universe]:
                del self.values[universe][channel]
                if not self.values[universe]:
                    del self.values[universe]
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
                    "hz": 30
                },
                "TcpSocket": {
                    "active": False,
                    "target_ip": "127.0.0.1",
                    "port": 7500,
                    "hz": 30
                }
            }
        self.artnet = None
        self.tcp_socket = None

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

    def configure_tcp_socket(self, active: bool, target_ip: str, port: int, hz: int) -> None:
        """
        Configures the TCP socket backend
        :param active: Whether the backend should be active
        :param target_ip: The target IP address
        :param port: The port to output to
        :param hz: The refresh rate
        :return: None
        """
        self.configuration["TcpSocket"]["active"] = active
        self.configuration["TcpSocket"]["target_ip"] = target_ip
        self.configuration["TcpSocket"]["port"] = port
        self.configuration["TcpSocket"]["hz"] = hz
        if active:
            self.tcp_socket = TcpSocketOutput(target_ip, port, hz)
        else:
            self.tcp_socket = None

    def set_values(self, values: list) -> None:
        """
        Outputs the values provided to the backend
        :param values: The values to output
        :return: None
        """
        if self.artnet:
            self.artnet.set_values(values)
        if self.tcp_socket:
            self.tcp_socket.set_values(values)

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
        self.active_snippets = []
        self.console_snippet = ConsoleOutputSnippet(self)

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
            relevant_snippets = self.active_snippets + [self.console_snippet]  # Always include the console snippet last
            for snippet in relevant_snippets:
                for snippet_universe in snippet.values:
                    if snippet_universe == universe:
                        for channel in snippet.values[universe]:
                            universe_values[channel - 1] = snippet.values[universe][channel]
            self.universes[universe].set_values(universe_values)

    def create_universe(self, universe_uuid: str, universe_name: str) -> None:
        """
        Creates a universe
        :param universe_uuid: The uuid of the universe
        :param universe_name: The name of the universe
        :return: None
        """
        self.universes[universe_uuid] = DmxUniverse(universe_uuid, universe_name)

    def remove_universe(self, universe_uuid: str) -> None:
        """
        Removes a universe
        :param universe_uuid: The uuid of the universe to remove
        :return: None
        """
        self.universes[universe_uuid].stop()
        del self.universes[universe_uuid]

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

    def configure_tcp_socket(self, universe_uuid: str, active: bool, target_ip: str, port: int, hz: int) -> None:
        """
        Configures the TCP socket backend for a universe
        :param universe_uuid: The uuid of the universe to configure
        :param active: Whether the backend should be active
        :param target_ip: The target IP address
        :param port: The port to output to
        :param hz: The refresh rate
        :return: None
        """
        universe = self.universes.get(universe_uuid)
        if universe is None:
            return
        universe.configure_tcp_socket(active, target_ip, port, hz)

    def write_output_configuration(self, configuration: dict) -> None:
        """
        Writes a whole configuration at once. This is used to load a configuration when opening a workspace.
        :param configuration: The configuration to write
        :return: None
        """
        for universe_uuid, universe_data in configuration.items():
            self.create_universe(universe_uuid, universe_data["name"])
            if universe_data.get("ArtNet"):
                self.configure_artnet(universe_uuid,
                        universe_data["ArtNet"].get("active", False),
                        universe_data["ArtNet"].get("target_ip", "127.0.0.1"),
                        universe_data["ArtNet"].get("universe", 0),
                        universe_data["ArtNet"].get("hz", 30))
            if universe_data.get("TcpSocket"):
                self.configure_tcp_socket(universe_uuid,
                        universe_data["TcpSocket"].get("active", False),
                        universe_data["TcpSocket"].get("target_ip", "127.0.0.01"),
                        universe_data["TcpSocket"].get("port", 7500),
                        universe_data["TcpSocket"].get("hz", 30))
            self.window.io_add_universe_entry(universe_uuid, universe_data["name"])

    def get_universe_configuration(self, universe_uuid: str) -> dict:
        """
        Gets the configuration of one universe
        :param universe_uuid: The uuid of the universe to get the configuration of
        :return: The configuration of the universe
        """
        return self.universes[universe_uuid].configuration

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
        for universe in self.universes:
            self.universes[universe].stop()
