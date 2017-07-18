# -*- coding: UTF-8 -*-
from abstractScoket import AbstractSocket
import re
import base64
import hashlib


class WebSocket(AbstractSocket):
    def ev_connect(self, conn): pass

    def ev_read(self, conn):
        _recv = conn.recv(1024)
        _send = self.hand_shake_response(_recv)
        if _send:
            conn.send(_send)
        else:
            return self.parse_data(_recv)

    def ev_write(self, conn, msg):
        conn.send(msg)

    def ev_hup(self, conn): pass

    @staticmethod
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

    @staticmethod
    def hand_shake_response(accept):
        match = re.search(r'Sec-WebSocket-Key: (\S+[=]{0,3})', accept)
        if match:
            print '新连接的响应'
            key = match.group(1)
            mask = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            token = base64.b64encode(hashlib.sha1(key + mask).digest())
            send = '\
HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n' % token
            return send



