# -*- coding: UTF-8 -*-
import socket
import base64
import hashlib
import re

def parse_data(msg):
    v = ord(msg[1]) & 0x7f
    if v == 0x7e:
        p = 4
    elif v == 0x7f:
        p = 10
    else:
        p = 2
    mask = msg[p:p + 4]
    data = msg[p + 4:]
    return ''.join([chr(ord(v) ^ ord(mask[k % 4])) for k, v in enumerate(data)])


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
            print '第一次连接!'
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

                print 'new websocket client joined!'
                reply = 'i got u, from websocket server.'
                length = len(reply)
                while True:
                    print '第二次连接!'
                    data = connection.recv(1024)
                    print parse_data(data)
                    connection.send('%c%c%s' % (0x81, length, reply))
        except socket.timeout:
            print 'websocket connection timeout'

