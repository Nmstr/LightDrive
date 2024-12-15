from stupidArtnet import StupidArtnet

class ArtnetOutput:
    def __init__(self, target_ip: str, artnet_universe: int, hz: int) -> None:
        """
        Creates the Artnet output class
        :param target_ip: The ip to output to
        :param artnet_universe: The artnet_universe to output to
        :param hz: The refresh rate
        """
        self.target_ip = target_ip
        self.artnet_universe = artnet_universe
        self.hz = hz
        self.packet_size = 512

        self.device = StupidArtnet(self.target_ip, self.artnet_universe, self.packet_size, self.hz, True, True)
        self.device.start()

    def set_single_value(self, channel: int, value: int) -> None:
        """
        Sets a single channel to another value
        :param channel: The channel to set
        :param value: The value that should be set
        :return: None
        """
        self.device.set_single_value(channel, value)
        self.device.show()

    def set_multiple_values(self, values: list[int]) -> None:
        """
        Sets all channels to a list of values
        :param values: The list of values (must match the packet size (512)
        :return: None
        """
        self.device.set(values)
        self.device.show()

    def stop(self) -> None:
        """
        Gracefully stops the output
        :return: None
        """
        self.device.blackout()
        self.device.stop()
        del self.device
