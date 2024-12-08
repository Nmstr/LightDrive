from .artnet import ArtnetOutput

class DmxOutput:
    def __init__(self) -> None:
        """
        Creates the output class to output data
        :param target_ip: The ip to output to
        :param universe: The universe to output to
        """
        self.packet_size = 512
        self.universes = {}
        self.output_configuration = {}

    def set_single_value(self, universe: int, channel: int, value: int) -> None:
        """
        Sets a single channel to another value
        :param universe: The universe to output to
        :param channel: The channel to set
        :param value: The value that should be set
        :return: None
        """
        if channel < 1 or channel > 512:
            print("ERROR: Channel out of range.")
            return
        backend = self.universes.get(universe)
        if backend is None:
            return
        backend.set_single_value(channel, value)

    def set_multiple_values(self, universe: int, values: list[int]) -> None:
        """
        Sets all channels to a list of values
        :param universe: The universe to output to
        :param values: The list of values (must match the packet size (512)
        :return: None
        """
        if len(values) != self.packet_size:
            print(f"ERROR: Packet size mismatch. Expected {self.packet_size} channels, got {len(values)}.")
            return
        backend = self.universes.get(universe)
        if backend is None:
            return
        backend.set_multiple_values(values)

    def blackout(self, universe: int) -> None:
        """
        Sets all channels to 0
        :param universe: The universe blackout
        :return: None
        """
        backend = self.universes.get(universe)
        if backend is None:
            return
        backend.blackout()

    def stop(self) -> None:
        """
        Gracefully stops the output
        :return: None
        """
        for universe in self.universes:
            self.universes.get(universe).stop()

    def setup_universe(self, universe: int, backend: str, **kwargs) -> None:
        """
        Sets up a universe
        :param universe: The universe to set up (minimum = 1)
        :param backend: The backend to choose
        :param kwargs: Additional arguments based on the backend
            - For "ArtNet" backend:
                - target_ip (str): The target IP address
                - artnet_universe (int): The ArtNet universe to use
        :return: None
        """
        if universe < 1:
            print("ERROR: Universe out of range.")
            return
        match backend:
            case "ArtNet":
                artnet = ArtnetOutput(kwargs["target_ip"], kwargs["artnet_universe"])
                self.universes[universe] = artnet
                self.output_configuration[universe] = [backend, kwargs]

    def remove_universe(self, universe: int) -> None:
        """
        Removes a specific universe
        :param universe: The universe to remove
        :return: None
        """
        backend = self.universes.get(universe)
        if backend is None:
            return
        backend.stop()
        self.universes.pop(universe)
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
                    self.setup_universe(universe=int(entry),
                                        backend="ArtNet",
                                        target_ip=configuration[entry][1]["target_ip"],
                                        artnet_universe=configuration[entry][1]["artnet_universe"])

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
