#!/usr/bin/env python

import socket
import threading
from itertools import takewhile


def http_response_data(status: int, status_msg: str, headers: dict, content: str = None):
    response_line = f"HTTP/1.1 {status} {status_msg}"
    if content:
        headers["Content-Length"] = len(bytes(content, 'utf-8'))
    header_lines = [f"{header_name}: {header_values}" for header_name, header_values in headers.items()]
    lines = [response_line, *header_lines, '']
    if content:
        lines.append(content)
    return bytes('\r\n'.join(lines), 'utf-8')


def serve_http(connection: socket.socket):
    def characters(sock):
        data = "initial data"
        while data:
            data = connection.recv(4096)
            for character in data:
                yield chr(character)

    def next_line(chars):
        line_characters = []
        for character in chars:
            line_characters.append(character)
            if len(line_characters) >= 2 and line_characters[-2] == '\r' and line_characters[-1] == '\n':
                break
        return ''.join(line_characters[:-2])

    with connection:
        request_chars = characters(connection)

        # get request line
        request_line = next_line(request_chars)
        method, request_uri, version = request_line.split()
        print(f"method = {method}\nuri = {request_uri}\nversion = {version}")

        # get headers
        headers = iter(lambda: next_line(request_chars), '')
        headers = map(lambda line: line.split(':', maxsplit=1), headers)
        headers = {header[0]: header[1].lstrip() for header in headers}
        print("Headers:\n", headers)

        if request_uri == '/ping':
            connection.sendall(http_response_data(200, 'OK', {"Content-type": "text/plain"}, "pong\n"))
        else:
            connection.sendall(http_response_data(404, "Not Found", {"Content-type": "text/plain"}, "Not found =(\n"))


def run_server(port, client_handler):
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(5)
        while True:
            in_connection, in_addr = server_socket.accept()
            print(f"Opened input connection with {in_addr}")
            threading.Thread(target=client_handler, args=[in_connection]).start()


if __name__ == '__main__':
    run_server(port=8080, client_handler=serve_http)
