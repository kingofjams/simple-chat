# -*- coding: UTF-8 -*-
import socket
import select
import Queue
import sys
import re
import base64
import hashlib
import json
import webSocket


class Worker:
    def __init__(self):
        self.running = 1
        webSocket.WebSocket()
