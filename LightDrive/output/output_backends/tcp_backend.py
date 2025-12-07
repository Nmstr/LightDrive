from output.output_backends.generic_output_backend import GenericOutputBackend#
import threading
import socket
import json

class TcpBackend(GenericOutputBackend):
    def __init__(self):
        super().__init__()
        self.connections = []

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('localhost', 8080))
        self.socket.listen()

        self.accept_thread = threading.Thread(target=self.accept_connection)
        self.accept_thread.daemon = True
        self.accept_thread.start()

    def accept_connection(self) -> None:
        while True:
            conn, addr = self.socket.accept()
            self.connections.append(conn)

    def set_values(self, values: list[int]) -> None:
        for conn in self.connections:
            try:
                conn.sendall(json.dumps(values).encode())
            except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError, BrokenPipeError):
                self.connections.remove(conn)

    def stop(self) -> None:
        for conn in self.connections:
            conn.close()
        self.socket.close()
