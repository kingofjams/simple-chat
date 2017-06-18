# -*- coding: UTF-8 -*-
import socket

user_id = 1111
user_name = ''
address = ('0.0.0.0', 8090)

_client1 = socket.socket()
_client1.connect(address)

