# -*- coding: UTF-8 -*-
global index
index = 4

user_list = {
    1: 'user1',
    2: 'user2',
    3: 'user3'
}
relation_user = {
    1: [2, 3],
    2: [1, 3],
    3: [1, 2],
}


def add_user(user_name):
    global index
    user_list.update({index: user_name})
    index += 1
    print user_list


def get_relation(user_id):
    return relation_user[user_id]


def add_relation(user_id, friend_user_id):
    if relation_user. has_key(user_id):
        relation_list = relation_user.get(user_id)
        if friend_user_id in relation_list:
            relation_list.append(friend_user_id)
            relation_user.update({user_id: relation_list})
    else:
        relation_user[user_id] = [user_id, friend_user_id]
    if relation_user. has_key(friend_user_id):
        relation_list = relation_user.get(friend_user_id)
        if user_id in relation_list:
            relation_list.append(user_id)
            relation_user.update({friend_user_id: relation_list})
    else:
        relation_user[friend_user_id] = [user_id, friend_user_id]


def del_relation(user_id, friend_user_id):
    if relation_user. has_key(user_id):
        relation_list = relation_user.get(user_id)
        if friend_user_id in relation_list:
            relation_list.remove(friend_user_id)
            relation_user.update({user_id: relation_list})
    if relation_user. has_key(friend_user_id):
        relation_list = relation_user.get(friend_user_id)
        if user_id in relation_list:
            relation_list.remove(user_id)
            relation_user.update({friend_user_id: relation_list})









