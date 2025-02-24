from PySide6.QtCore import QTimer
import threading
import socket
import json

class TcpSocketOutput:
    def __init__(self, target_ip: str, port: int, hz: int) -> None:
        """
        Creates a TCP socket output class
        :param target_ip: The ip to output to
        :param port: The port to output to
        :param hz: The refresh rate
        """
        self.target_ip = target_ip
        self.port = port
        self.packet_size = 512
        self.output_values = [0] * self.packet_size
        self.connections = []

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.target_ip, self.port))
        self.socket.listen()
        print("Server listening on", self.target_ip, ":", self.port)

        self.accept_thread = threading.Thread(target=self.accept_connections)
        self.accept_thread.daemon = True
        self.accept_thread.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.send_data)
        self.timer.start(1000 // hz)

    def accept_connections(self) -> None:
        """
        Accepts incoming connections in a separate thread
        :return: None
        """
        while True:
            conn, addr = self.socket.accept()
            self.connections.append(conn)

    def send_data(self) -> None:
        """
        Sends the data to all connected clients
        :return: None
        """
        data = json.dumps(self.output_values).encode('utf-8')
        for conn in self.connections:
            try:
                conn.sendall(data)
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError):
                self.connections.remove(conn)

    def set_values(self, values: list[int]) -> None:
        """
        Sets all channels to a list of values
        :param values: The list of values (must match the packet size (512)
        :return: None
        """
        self.output_values = values

    def stop(self) -> None:
        """
        Gracefully stops the output
        :return: None
        """
        self.timer.stop()
        for conn in self.connections:
            conn.close()
        self.socket.close()
