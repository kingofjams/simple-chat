# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod


class AbsEvent(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def ev_connect(self):
        print('触发连接事件\n')
        pass

    @abstractmethod
    def ev_read(self):
        print('触发读事件\n')
        pass

    @abstractmethod
    def ev_write(self):
        print('触发写事件\n')
        pass

    @abstractmethod
    def ev_hup(self):
        print('触发断开连接事件\n')
        pass

