# coding=utf-8
import time

import datetime

import handlers
import transaction as journal
import twx.botapi as tel

token = ''
bot = tel.TelegramBot(token, request_method=tel.RequestMethod.GET)
bot.update_bot_info().wait()
users = []


class User:
    def __init__(self, _id, name, action=handlers.ACTION.Empty):
        self.balance_trans = journal.Transaction(_id, '$yhg', datetime.datetime.now(), 0)
        self.id = _id
        self.name = name
        self.action = action
        self.value = 0
        self.balance = 0
        self.currency = 'руб'


def find_user(_id):
    for u in users:
        if u.id == _id:
            return u


def add(_users, user):
    for u in _users:
        if u.id == user.id:
            return
    users.append(user)
    journal.pool[user.id].append(user.balance_trans)


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
    current_id = None
    while True:
        try:
            updates = bot.get_updates(offset=current_id).wait() or []
            for update in updates:
                current_id = update.update_id + 1
                msg = update.message
                _user = User(msg.sender.id, '%s %s' % (msg.sender.first_name, msg.sender.last_name))
                add(users, _user)

                print('"%s" from %s' % (msg.text, _user.name))
                handle(find_user(_user.id), msg)
            if not len(updates):
                time.sleep(0.1)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
