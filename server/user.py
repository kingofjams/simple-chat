# -*- coding: UTF-8 -*-
from db import dbUser


class User:
    users = {}

    def __init__(self, user_id):
        # 初始化
        self.online = 0
        self.connection = object
        self.user_id = user_id
        self.users[user_id] = self

    def on_login(self, connection):
        self.connection = connection
        self.online = 1

    def add_friend(self, friend_id):
        dbUser.add_relation(self.user_id, friend_id)

    def login_out(self):
        self.users.pop(self.user_id)

    def get_friend(self):
        dbUser.get_relation(self.user_id)

    def del_friend(self, friend_id):
        dbUser.del_relation(self.user_id, friend_id)


