# -*- coding: UTF-8 -*-
import socket
import select
import Queue


class Worker:
    workers = []

    def __init__(self):
        self.ip = '0.0.0.0'
        self.port = 8090
        self.workers.append('a')
        self.time_out = 10
        # 这里epoll只能在linux下才能使用
        self.epoll = select.epoll(self.time_out)
        self.message_queues = {}
        self.fd_to_socket = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.create_socket()
        self.ep_read()

    def create_socket(self):
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

    def ep_read(self):
        while True:
            print "等待活动连接......"
            events = self.epoll.poll(self.time_out)
            if not events:
                print "epoll超时无活动连接， 重新轮询......"
            else:
                print "有", len(events), "个新事件， 开始处理......"
                for fd, event in events:
                    _socket = self.fd_to_socket[fd]
                    if _socket == self.server_socket:
                        connection, address = self.server_socket.accept()
                        print "新连接:", address
                        connection.setblocking(False)
                        self.epoll.register(connection.fileno, select.EPOLLIN)
                        self.fd_to_socket[connection.fileno] = connection
                        self.message_queues[connection] = Queue.Queue()
                    elif event & select.EPOLLHUP:
                        print '客户端已经关闭连接'
                        # 注销客户句炳
                        self.epoll.unregister(fd)
                        self.fd_to_socket[fd].close()
                        del [fd]
                    elif event & select.EPOLLIN:
                        data = _socket.recv(1024)
                        if data:
                            print "收到数据:", data, "客户端:", _socket.getpeername()
                            self.message_queues[socket].put(data)
                            self.epoll.modify(fd, select.EPOLLOUT)
                        elif event & select.EPOLLOUT:
                            try:
                                msg = self.message_queues[socket].get_nowait()
                            except Queue.Empty:
                                print _socket.getpeername(), "queue empty"
                                self.epoll.modify(fd, select.EPOLLIN)
                            else:
                                print "发送数据：", data, "客户端:", _socket.getpeername()
                                _socket.send(msg)

    def close(self):
        self.epoll.unregister(self.server_socket.fileno())
        self.epoll.close()
        self.server_socket.close()


