#!/usr/bin/env python

import socket
import threading


def run_echo_server():
    def echo(connection: socket.socket):
        with connection:
            while True:
                data = connection.recv(1024)
                if data:
                    connection.sendall(data)
                else:
                    return

    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('0.0.0.0', 8080))
        server_socket.listen(5)
        while True:
            in_connection, in_addr = server_socket.accept()
            print(f"Opened input connection with {in_addr}")
            threading.Thread(target=echo, args=[in_connection]).start()


if __name__ == '__main__':
    run_echo_server()
