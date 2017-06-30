# -*- coding: UTF-8 -*-
import socket
import select
import sys
from abc import ABCMeta, abstractmethod


class AbstractSocket(object):
    __metaclass__ = ABCMeta

    def __init__(self, ip='0.0.0.0', port=8090):
        self.ip = ip
        self.port = port
        self.time_out = 10
        self.epoll = select.epoll(self.time_out)
        self.fd_conn = []
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception, e:
            sys.stdout.write('fork #1 failed: (%s)\n' % str(e))
            sys.exit(1)
        self.create_socket()
        self.ep_read()

    def create_socket(self):
        try:
            # SO_REUSEADDR 端口被释放后立即使用
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_address = (self.ip, self.port)
            self.server_socket.bind(server_address)
            self.server_socket.listen(10)
            self.server_socket.setblocking(False)
            # 注册服务器监听fd到等待读事件集合
            # EPOLLIN 端口释放后立即启用
            self.epoll.register(self.server_socket.fileno(), select.EPOLLIN)
        except Exception, e:
            sys.stdout.write('创建socket失败! %s\n' % str(e))

    def ep_read(self):
        while True:
            events = self.epoll.poll(10)
            if not events:
                print '现在还没有事件，等待10秒进行下一次循环'
                continue
            for fd, event in events:
                if fd == self.server_socket.fileno():
                    conn = self.server_socket.accept()
                    fd = conn.fileno()
                    self.fd_conn[fd] = conn
                    self.ev_connect(conn)
                    self.epoll.register(fd, select.EPOLLIN)
                elif event & select.EPOLLHUP:
                    conn = self.ev_hup[fd]
                    conn.close()
                    self.fd_conn.pop(fd)
                    self.ev_hup(conn)
                elif event & select.EPOLLIN:
                    conn = self.fd_conn[fd]
                    self.ev_read(conn)
                    self.epoll.register(fd, select.EPOLLIN)
                elif event & select.EPOLLOUT:
                    conn = self.fd_conn[fd]
                    self.ev_write(conn)

    def close(self):
        self.epoll.unregister(self.server_socket.fileno())
        self.epoll.close()
        self.server_socket.close()

    @abstractmethod
    def ev_connect(self, conn): pass

    @abstractmethod
    def ev_read(self, conn): pass

    @abstractmethod
    def ev_write(self, conn, msg): pass

    @abstractmethod
    def ev_hup(self, conn): pass

