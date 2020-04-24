import datetime
import typing

import handlers
from transaction import Transaction, pool

users: typing.List = []


class User:

    @classmethod
    def users(cls):
        return users

    @staticmethod
    def save():
        from storage import save_users
        save_users(build_users())

    def __init__(self, _id, name, action=handlers.ACTION.Empty):
        self.balance_trans = Transaction(_id, '$yhg', datetime.datetime.now(), 0)
        self.id = _id
        self.name = name
        self.action = action
        self.value = 0
        self.balance = 0
        self.currency = 'руб'
        pool.get(_id, []).append(self.balance_trans)


def find_user(_id):
    for u in User.users():
        if u.id == _id:
            return u


def build_users() -> typing.List[typing.Dict]:
    from storage import build_user
    _users = [build_user(u) for u in User.users()]
    return _users


def add(user):
    for u in users:
        if u.id == user.id:
            return
    User.users().append(user)
