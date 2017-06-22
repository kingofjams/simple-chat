# -*- coding: UTF-8 -*-
import socket
import select
import Queue
import sys
import re
import base64
import hashlib


class Worker:
    workers = []
    ip = '0.0.0.0'
    port = 8090
    time_out = 10

    def __init__(self):
        # 开新的进程
        # try:
        #     pid = os.fork()
        #     if pid > 0:
        #         sys.exit(0)
        # except OSError, e:
        #     sys.stdout.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
        #     sys.exit(1)
        # self.workers.append(pid)
        # 这里epoll只能在linux下才能使用
        self.epoll = select.epoll(self.time_out)
        self.message_queues = {}
        self.fd_to_socket = {}
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
            # 文件句柄到所对应对象的字典，格式为{句柄：对象}
            self.fd_to_socket = {self.server_socket.fileno(): self.server_socket, }
        except Exception, e:
            sys.stdout.write('创建socket失败! %s\n' % str(e))

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

    def ep_read(self):
        while True:
            events = self.epoll.poll(10)
            if not events:
                print '现在还没有新的事件, 10秒后进行下一次循环'
                continue
            for fd, event in events:
                print 'event:', event
                event_socket = self.fd_to_socket[fd]
                if event_socket == self.server_socket:
                    print '有新的连接'
                    _connection, address = event_socket.accept()
                    _connection_fd = _connection.fileno()
                    _connection.setblocking(False)
                    self.fd_to_socket[_connection_fd] = _connection
                    self.message_queues[_connection] = Queue.Queue()
                    print 'connect fd', _connection_fd
                    print 'connect address', address
                    self.epoll.register(_connection_fd, select.EPOLLIN)
                elif event & select.EPOLLHUP:
                    print '客户断已经断开连接'
                    self.epoll.unregister(fd)
                    event_socket.close()
                    del event_socket[fd]
                    print '删除注册表'
                    exit(0)
                elif event & select.EPOLLIN:
                    print 'in fd', fd
                    print '有可读的事件触发'
                    _accept = event_socket.recv(1024)
                    if _accept:
                        match = re.search(r'Sec-WebSocket-Key: (\S+[=]{0,3})', _accept)
                        if match:
                            print '新连接的响应'
                            key = match.group(1)
                            mask = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                            token = base64.b64encode(hashlib.sha1(key + mask).digest())
                            event_socket.send('\
HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n' % token)
                        else:
                            _accept = self.parse_data(_accept)
                            print '读到的信息为:', _accept
                            self.message_queues[event_socket].put(_accept)
                            self.epoll.modify(fd, select.EPOLLOUT)
                    else:
                        print '断开连接'
                        self.epoll.modify(fd, select.EPOLLHUP)
                        self.epoll.unregister(fd)
                        event_socket.close()
                        del event_socket
                elif event & select.EPOLLOUT:
                    print '发送数据。。。'
                    _send = self.message_queues[event_socket].get_nowait()
                    event_socket.send('%c%c%s' % (0x81, len(_send), _send))
                    self.epoll.modify(fd, select.EPOLLIN)

    def close(self):
        self.epoll.unregister(self.server_socket.fileno())
        self.epoll.close()
        self.server_socket.close()

Worker()
