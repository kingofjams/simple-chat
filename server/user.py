# -*- coding: UTF-8 -*-
from db import dbUser

class User:
    user_obj = {}

    def __init__(self, user_id):
        # 初始化
        self.online = 0
        self.user_id = user_id
        user_id[user_id] = self

    def get_friend(self):
        dbUser.
        return


