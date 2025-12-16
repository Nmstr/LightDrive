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
        self.lock = threading.Lock()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.target_ip, self.port))
        except OSError:
            print("Failed to bind to port")
        self.socket.listen()

        self.accept_running = True
        self.accept_thread = self.create_accept_thread()
        self.accept_thread.start()

        self.output_timer = QTimer()
        self.output_timer.setInterval(int(1000 / hz))
        self.output_timer.timeout.connect(lambda: self.send_values())
        self.output_timer.start()

    def create_accept_thread(self) -> threading.Thread:
        self.accept_thread = threading.Thread(target=self.accept_connection)
        self.accept_thread.daemon = True
        self.accept_running = True
        return self.accept_thread

    def accept_connection(self) -> None:
        while self.accept_running:
            try:
                conn, addr = self.socket.accept()
                with self.lock:
                    self.connections.append(conn)
            except OSError:
                break

    def set_values(self, values: list[int]) -> None:
        self.values = values

    def send_values(self) -> None:
        with self.lock:
            for conn in self.connections:
                try:
                    conn.sendall(json.dumps(self.values).encode())
                except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError, BrokenPipeError, OSError):
                    try:
                        conn.close()
                    except OSError:
                        pass
                    self.connections.remove(conn)

    def stop(self) -> None:
        with self.lock:
            for conn in self.connections:
                try:
                    conn.close()
                except OSError:
                    pass
            self.connections.clear()
            self.socket.shutdown(socket.SHUT_RDWR)

    def update_configuration(self, target_ip: str, port: int, hz: int) -> None:
        if target_ip != self.target_ip or port != self.port:
            self.target_ip = target_ip
            self.port = port

            self.output_timer.stop()
            self.accept_running = False

            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                new_socket.bind((self.target_ip, self.port))
            except OSError:
                print("Failed to bind to port")
            new_socket.listen()

            self.stop()
            self.accept_thread.join()

            self.socket = new_socket
            self.accept_thread = self.create_accept_thread()
            self.accept_thread.start()

            self.output_timer.start()
        if hz != self.hz:
            self.hz = hz
            self.output_timer.setInterval(int(1000 / hz))
