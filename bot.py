# coding=utf-8
import time

import datetime
import typing

import handlers
import transaction as journal
import twx.botapi as tel

from users import User, add, find_user

token = ''
bot = tel.TelegramBot(token, request_method=tel.RequestMethod.GET)
bot.update_bot_info().wait()


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
                add(_user)

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
