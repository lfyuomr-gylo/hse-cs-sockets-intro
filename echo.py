#!/usr/bin/env python

import socket
import threading
from pathlib import Path
from typing import Union

CONTENT_DIR = Path(__file__).absolute().parent / 'static_data'


def http_response_data(status: int, status_msg: str, headers: dict, content: Union[str, bytes] = None):
    response_line = f"HTTP/1.1 {status} {status_msg}"
    if isinstance(content, str):
        content = bytes(content, 'utf-8')
    if content:
        headers["Content-Length"] = len(content)
    header_lines = [f"{header_name}: {header_values}" for header_name, header_values in headers.items()]
    lines = [response_line, *header_lines]
    return bytes('\r\n'.join(lines), 'utf-8') + 2 * b'\r\n' + content


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

        content_file = CONTENT_DIR / request_uri.lstrip('/')
        if content_file.exists():
            with content_file.open('r'):
                response_payload = content_file.read_bytes()
                response_data = http_response_data(200, "OK", {}, content=response_payload)
                connection.sendall(response_data)
        else:
            connection.sendall(http_response_data(404, "Not Found", {}, content=f"File {content_file} does not exist"))


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
