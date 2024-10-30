from artnet import ArtnetOutput

class DmxOutput:
    def __init__(self, target_ip: str, universe: int) -> None:
        """
        Creates the output class to output data
        :param target_ip: The ip to output to
        :param universe: The universe to output to
        """
        self.packet_size = 512
        self.artnet = ArtnetOutput(target_ip, universe)

    def set_single_value(self, channel: int, value: int) -> None:
        """
        Sets a single channel to another value
        :param channel: The channel to set
        :param value: The value that should be set
        :return: None
        """
        if channel < 1 or channel > 512:
            print("ERROR: Channel out of range.")
            return
        self.artnet.set_single_value(channel, value)

    def set_multiple_values(self, values: list[int]) -> None:
        """
        Sets all channels to a list of values
        :param values: The list of values (must match the packet size (512)
        :return: None
        """
        if len(values) != self.packet_size:
            print(f"ERROR: Packet size mismatch. Expected {self.packet_size} channels, got {len(values)}.")
            return
        self.artnet.set_multiple_values(values)

    def blackout(self) -> None:
        """
        Sets all channels to 0
        :return: None
        """
        self.artnet.blackout()

    def stop(self) -> None:
        """
        Gracefully stops the output
        :return: None
        """
        self.artnet.stop()
