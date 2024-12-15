from .artnet import ArtnetOutput

class OutputSnippet:
    def __init__(self, dmx_output, values: dict) -> None:
        """
        Creates a snippet
        :param dmx_output: An instance of the DmxOutput class (used to tick the output after updating values)
        :param values: The values to set (dict of channel: value pairs)
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

class DmxOutput:
    def __init__(self) -> None:
        """
        Creates the output class to output data
        """
        self.output_configuration = {}
        self.universes = {}
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

    def tick_output(self) -> None:
        """
        Ticks the output updating values in the backends
        :return: None
        """
        for universe in self.universes:
            universe_values = [0] * 512
            for snippet in self.active_snippets:
                for channel in snippet.values:
                    universe_values[channel - 1] = snippet.values[channel]
            for backend in self.universes[universe]:
                backend.set_multiple_values(universe_values)

    def setup_backend(self, universe: int, backend: str, **kwargs) -> None:
        """
        Sets up a backend
        :param universe: The universe for the new backend
        :param backend: The backend to choose
        :param kwargs: Additional arguments based on the backend
            - For "ArtNet" backend:
                - target_ip (str): The target IP address
                - artnet_universe (int): The ArtNet universe to use
                - hz (int): The refresh rate
        :return: None
        """
        if universe not in self.universes:
            self.universes[universe] = []

        if backend == "ArtNet":
            artnet = ArtnetOutput(kwargs["target_ip"], kwargs["artnet_universe"], kwargs["hz"])
            self.universes[universe].append(artnet)
            self.output_configuration[universe] = [backend, kwargs]

    def remove_backend(self, universe: int, backend: str) -> None:
        """
        Removes a backend from a universe
        :param universe: The universe to remove the backend from
        :param backend: The backend to remove
        :return: None
        """
        if universe in self.universes:
            for i, backend_instance in enumerate(self.universes[universe]):
                if isinstance(backend_instance, ArtnetOutput):
                    self.universes[universe].pop(i)
                    self.output_configuration.pop(universe)

    def write_universe_configuration(self, configuration: dict) -> None:
        """
        Writes a whole universe configuration. This is used to load a configuration when loading a workspace
        :param configuration: The configuration to write
        :return: None
        """
        for entry in configuration:
            match configuration[entry][0]:
                case "ArtNet":
                    self.setup_backend(universe=int(entry),
                                       backend="ArtNet",
                                       target_ip=configuration[entry][1]["target_ip"],
                                       artnet_universe=configuration[entry][1]["artnet_universe"],
                                       hz=configuration[entry][1]["hz"])

    def get_universe_data(self, universe: int) -> dict:
        """
        Gets the data about a specific universe
        :param universe: The universe to get the data from
        :return: The data about the universe
        """
        universe_data = self.output_configuration.get(universe)
        if universe_data is None:
            return {}
        return universe_data

    def shutdown_output(self) -> None:
        """
        Gracefully stops all backends
        :return: None
        """
        for universe in self.universes:
            for backend in self.universes[universe]:
                backend.stop()
