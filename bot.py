# coding=utf-8
import time

import datetime
import typing

import handlers
import transaction as journal
import twx.botapi as tel

token = ''
bot = tel.TelegramBot(token, request_method=tel.RequestMethod.GET)
bot.update_bot_info().wait()


class User:
    _users: typing.List["User"] = []

    @classmethod
    def users(cls):
        return cls._users

    @staticmethod
    def save():
        print("26 ", User.users())
        from storage import save_users
        save_users(build_users())

    def __init__(self, _id, name, action=handlers.ACTION.Empty):
        self.balance_trans = journal.Transaction(_id, '$yhg', datetime.datetime.now(), 0)
        self.id = _id
        self.name = name
        self.action = action
        self.value = 0
        self.balance = 0
        self.currency = 'руб'
        journal.pool.get(_id, []).append(self.balance_trans)


def find_user(_id):
    print("find ", User.users())
    for u in User.users():
        if u.id == _id:
            return u


def build_users() -> typing.List[typing.Dict]:
    print("49 ", User.users())
    from storage import build_user
    print("51 ", User.users())
    users = [build_user(u) for u in User.users()]
    return users


def add(users, user):
    print("add ", users)
    for u in users:
        if u.id == user.id:
            return
    User.users().append(user)


def handle(user, message):
    rm = tel.ReplyKeyboardRemove.create()
    try:
        answer, keyboard = handlers.handle(user, message.text)
        print(answer, keyboard)

        if keyboard:
            rm = tel.ReplyKeyboardMarkup.create(keyboard)
        if answer:
            if isinstance(answer, str):
                bot.send_message(user.id, answer, reply_markup=rm)
            else:
                bot.send_photo(user.id, answer, reply_markup=rm)
        else:
            bot.send_message(user.id, 'Я не могу понять что ты от меня хочешь', reply_markup=rm)
    except Exception as e:
        print(e)


def main():
    load()

    current_id = None
    while True:
        try:
            updates = bot.get_updates(offset=current_id).wait() or []
            for update in updates:
                current_id = update.update_id + 1
                msg = update.message
                _user = User(msg.sender.id, '%s %s' % (msg.sender.first_name, msg.sender.last_name))
                add(User.users(), _user)

                print('"%s" from %s' % (msg.text, _user.name))
                handle(find_user(_user.id), msg)
            if not len(updates):
                time.sleep(0.1)
        except Exception as e:
            print(e)


def load():
    from storage import load_users, load_pool
    users = load_users()
    User.users().extend(users)
    _pool = load_pool()
    journal.pool = _pool
    print('load!')


if __name__ == '__main__':
    main()
