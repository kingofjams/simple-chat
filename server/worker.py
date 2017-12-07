# -*- coding: UTF-8 -*-
import socket
import select
import sys
import os
import re
import base64
import hashlib
import json
from webSocket import WebSocket


class Worker:
    workers = []

    def __init__(self):
        self.pid = 0
        self.fork_one_worker()
        self.workers.append(self)

    def fork_one_worker(self):
        try:
            pid = os.fork()
        except OSError as e:
            sys.stdout.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)
        if pid > 0:
            self.pid = pid
            WebSocket('0.0.0.0', 8090)

