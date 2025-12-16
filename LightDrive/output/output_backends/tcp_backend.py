from output.output_backends.generic_output_backend import GenericOutputBackend
from PySide6.QtCore import QTimer
import threading
import socket
import json

class TcpBackend(GenericOutputBackend):
    def __init__(self, target_ip: str, port: int, hz: int):
        super().__init__()
        self.target_ip = target_ip
        self.port = port
        self.hz = hz
        self.connections = []
        self.values = [0] * 512

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.target_ip, self.port))
        except OSError:
            print("Failed to bind to port")
        self.socket.listen()

        self.accept_thread = threading.Thread(target=self.accept_connection)
        self.accept_thread.daemon = True
        self.accept_thread.start()

        self.output_timer = QTimer()
        self.output_timer.setInterval(int(1000 / hz))
        self.output_timer.timeout.connect(lambda: self.send_values())
        self.output_timer.start()

    def accept_connection(self) -> None:
        while True:
            conn, addr = self.socket.accept()
            self.connections.append(conn)

    def set_values(self, values: list[int]) -> None:
        self.values = values

    def send_values(self) -> None:
        for conn in self.connections:
            try:
                conn.sendall(json.dumps(self.values).encode())
            except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError, BrokenPipeError):
                self.connections.remove(conn)

    def stop(self) -> None:
        for conn in self.connections:
            conn.close()
        self.socket.close()
