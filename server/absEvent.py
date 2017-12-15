# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod


class AbsEvent(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def ev_connect(self, conn): pass

    @abstractmethod
    def ev_read(self, conn): pass

    @abstractmethod
    def ev_write(self, conn, msg): pass

    @abstractmethod
    def ev_hup(self, conn): pass

