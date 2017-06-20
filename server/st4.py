# -*- coding: UTF-8 -*-
import socket
import select
import struct
import hashlib
import Queue
import re


def generate_token(key1, key2, key3):
    num1 = int("".join([digit for digit in list(key1) if digit.isdigit()]))
    spaces1 = len([char for char in list(key1) if char == " "])
    num2 = int("".join([digit for digit in list(key2) if digit.isdigit()]))
    spaces2 = len([char for char in list(key2) if char == " "])
    combined = struct.pack(">II", num1 / spaces1, num2 / spaces2) + key3
    return hashlib.md5(combined).digest()


def on_open_safari_response(_recv):
    headers = {}
    if _recv.find('\r\n\r\n') != -1:
        header, data = _recv.split('\r\n\r\n', 1)
        for line in header.split("\r\n")[1:]:
            key, value = line.split(": ", 1)
            headers[key] = value
        headers["Location"] = "ws://0.0.0.0:8090"
        key1 = headers["Sec-WebSocket-Key1"]
        key2 = headers["Sec-WebSocket-Key2"]
        if len(data) < 8:
            data += _recv(8 - len(data))
        key3 = data[:8]
        token = generate_token(key1, key2, key3)
        handshake = '\
            HTTP/1.1 101 Web Socket Protocol Handshake\r\n \
            Upgrade: WebSocket\r\n \
            Connection: Upgrade\r\n \
            Sec-WebSocket-Origin: %s\r\n \
            Sec-WebSocket-Location: %s\r\n\r\n \
            ' % (headers['Origin'], headers['Location'])
        print '返回客户端的信息：', handshake + token
        return handshake + token
    else:
        print '返回客户端的信息：', _recv
        return _recv


def on_open_chrome_response(_recv):
    handshake = '\
        HTTP/1.1 101 Web Socket Protocol Handshake\r\n \
        Upgrade: WebSocket\r\n \
        Connection: Upgrade\r\n \
        Sec-WebSocket-Accept: %s\r\n \
        Sec-WebSocket-Protocol: %s\r\n\r\n \
        ' %


if __name__ == '__main__':
    fd_socket = {}

    por = select.epoll()
    _server = socket.socket()
    address = ('0.0.0.0', 8090)
    _server.bind(address)
    _server.listen(5)
    _server.setblocking(False)
    main_fd = _server.fileno()
    fd_socket[main_fd] = _server
    por.register(main_fd, select.EPOLLIN)
    queue_msg = {}

    while True:
        events = por.poll(10)
        if not events:
            print '现在还没有新的事件, 10秒后进行下一次循环'
            continue

        for fd, event in events:
            print 'event:', event
            event_socket = fd_socket[fd]
            if event_socket == _server:
                print '有新的连接'
                _connection, address = _server.accept()
                _connection_fd = _connection.fileno()
                _connection.setblocking(False)
                fd_socket[_connection_fd] = _connection
                queue_msg[_connection] = Queue.Queue()
                print 'connect fd', _connection_fd
                print 'connect address', address
                por.register(_connection_fd, select.EPOLLIN)
            elif event & select.EPOLLHUP:
                print '客户断已经断开连接'
                por.unregister(fd)
                event_socket.close()
                del fd_socket[fd]
                print '删除注册表'
                exit(0)
            elif event & select.EPOLLIN:
                print 'in fd', fd
                print '有可读的事件触发'
                _accept = event_socket.recv(1024)
                if _accept:
                    print '读到的信息为:' , _accept
                    queue_msg[fd_socket[fd]].put(_accept)
                    por.modify(fd, select.EPOLLOUT)
                else:
                    print '断开连接'
                    por.modify(fd, select.EPOLLHUP)
                    por.unregister(fd)
                    event_socket.close()
                    del fd_socket[fd]
            elif event & select.EPOLLOUT:
                print '发送数据。。。'
                _send = on_open_response(queue_msg[fd_socket[fd]].get_nowait())
                fd_socket[fd].send('nid')
                por.modify(fd, select.EPOLLIN)








