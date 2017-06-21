# -*- coding: UTF-8 -*-
import socket
import base64
import hashlib
import re
import threading


class websocket_thread(threading.Thread):
    def __init__(self, connection):
        super(websocket_thread, self).__init__()
        self.connection = connection

    def run(self):
        print 'new websocket client joined!'
        reply = 'i got u, from websocket server.'
        length = len(reply)
        while True:
            data = self.connection.recv(1024)
            self.connection.send('%c%c%s' % (0x81, length, reply))


def on_open_chrome_response(connection, _recv):
    match = re.search(r'Sec-WebSocket-Key: (\S+[=]{0,3})', _recv)
    if match:
        key = match.group(1)
        mask = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        token = base64.b64encode(hashlib.sha1(key + mask).digest())
        connection.send('\
        HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
        Upgrade: WebSocket\r\n\
        Connection: Upgrade\r\n\
        Sec-WebSocket-Accept: %s\r\n\r\n' % token)


def parse_headers(msg):
    headers = {}
    header, data = msg.split('\r\n\r\n', 1)
    for line in header.split('\r\n')[1:]:
        key, value = line.split(': ', 1)
        headers[key] = value
    headers['data'] = data
    return headers


def generate_token(msg):
    key = msg + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    ser_key = hashlib.sha1(key).digest()
    return base64.b64encode(ser_key)

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 8090))
    sock.listen(5)
    while True:
        connection, address = sock.accept()
        try:
            recvdata = connection.recv(1024)
            match = re.search(r'Sec-WebSocket-Key: (\S+[=]{0,3})', recvdata)
            if match:
                key = match.group(1)
                mask = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                token = base64.b64encode(hashlib.sha1(key + mask).digest())
                connection.send('\
HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n' % token)
                thread = websocket_thread(connection)
                thread.start()
        except socket.timeout:
            print 'websocket connection timeout'

