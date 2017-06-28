# -*- coding: UTF-8 -*-

class DbUser:
    # 用户名称
    user_list = {
        1 : 'user1',
        2 : 'user2',
        3 : 'user3'
    }
    # 关系表
    relation_user = {
            1 : {2,3},
            2 : {1,3},
            3 : {1,2},
        }

    @staticmethod
    def get_friend(user_id):
        relation_user.append('fsdfs')
        return relation_user[user_id]



        user_list.add(user_name)


    def add_user(user_name)





