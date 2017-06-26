# -*- coding: UTF-8 -*-
import socket
import select
import Queue
import sys
import re
import base64
import hashlib
import json
import os


class worker1:
    # 新建一个进程
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stdout.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)
    self.workers.append(pid)