# -*- coding: UTF-8 -*-
import socket
import select
import base64
import hashlib
import Queue
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
                por.register(_connection_fd, select.EPOLLIN)
            elif event & select.EPOLLHUP:
                print '客户断已经断开连接'
                por.unregister(fd)
                event_socket.close()
                del event_socket
                print '删除注册表'
                exit(0)
            elif event & select.EPOLLIN:
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
                        _accept = parse_data(_accept)
                        print '读到的信息为:', _accept
                        queue_msg[event_socket].put(_accept)
                        por.modify(fd, select.EPOLLOUT)
                else:
                    print '断开连接'
                    por.modify(fd, select.EPOLLHUP)
                    por.unregister(fd)
                    event_socket.close()
                    del event_socket
            elif event & select.EPOLLOUT:
                print '发送数据。。。'
                _send = queue_msg[event_socket].get_nowait()
                event_socket.send('%c%c%s' % (0x81, len(_send), _send))
                por.modify(fd, select.EPOLLIN)








