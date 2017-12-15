# -*- coding: UTF-8 -*-
import queue
import sys
from select import select
from absEvent import AbsEvent
import socket


class XtSelect:

    def __init__(self, ip='0.0.0.0', port=8090):
        self.ip = ip
        self.port = port
        self.output_list = []
        self.input_list = []
        self.message_queue = {}
        self.create_socket()
        self.ep_read()
        self.server_socket = socket.socket()

    def create_socket(self):
        try:
            # SO_REUSEADDR 端口被释放后立即使用
            server_address = (self.ip, self.port)
            self.server_socket.bind(server_address)
            self.server_socket.listen(10)
            self.server_socket.setblocking(False)
            # 初始化将服务端加入监听列表
            self.input_list.append(self.server_socket)
        except Exception as e:
            sys.stdout.write('创建socket失败! %s\n' % str(e))

    def ep_read(self):
        while True:
            # 开始 select 监听,对input_list中的服务端server进行监听
            stdinput, stdoutput, stderr = select(self.input_list, self.output_list, self.input_list)
            for obj in stdinput:
                if obj == self.server_socket:
                    # 接收客户端的连接, 获取客户端对象和客户端地址信息
                    conn, addr = self.server_socket.accept()
                    # 将客户端对象也加入到监听的列表中, 当客户端发送消息时 select 将触发
                    self.input_list.append(conn)
                    # 为连接的客户端单独创建一个消息队列，用来保存客户端发送的消息
                    self.message_queue[conn] = queue.Queue()
                    AbsEvent.ev_connect(conn)
                else:
                    # 由于客户端连接进来时服务端接收客户端连接请求，将客户端加入到了监听列表中(input_list)，客户端发送消息将触发
                    # 所以判断是否是客户端对象触发
                    try:
                        if obj not in self.output_list:
                            self.output_list.append(obj)
                        AbsEvent.ev_read(obj)
                    except ConnectionResetError:
                        # 客户端断开连接了，将客户端的监听从input列表中移除
                        self.input_list.remove(obj)
                        # 移除客户端对象的消息队列
                        del self.message_queue[obj]
                        print("\n[input] Client  {0} disconnected".format(addr))

                        # 如果现在没有客户端请求,也没有客户端发送消息时，开始对发送消息列表进行处理，是否需要发送消息
            for sendobj in self.output_list:
                try:
                    # 如果消息队列中有消息,从消息队列中获取要发送的消息
                    if not self.message_queue[sendobj].empty():
                        # 从该客户端对象的消息队列中获取要发送的消息
                        send_data = self.message_queue[sendobj].get()
                        sendobj.sendall(send_data)
                    else:
                        # 将监听移除等待下一次客户端发送消息
                        self.output_list.remove(sendobj)

                except ConnectionResetError:
                    # 客户端连接断开了
                    del self.message_queue[sendobj]
                    self.output_list.remove(sendobj)
                    print("\n[output] Client  {0} disconnected".format(addr))

if __name__ == '__main__':
    st = XtSelect()



