# coding=utf-8
import time
import handlers
import twx.botapi as tel

token = '184993535:AAGdIgccMjPGHrXSjStqqJAf8eSyeEYnTas'
bot = tel.TelegramBot(token, request_method=tel.RequestMethod.GET)
bot.update_bot_info().wait()
users = []


class User(object):
    def __init__(self, _id, name, action=handlers.ACTION.Empty):
        self.id = _id
        self.name = name
        self.action = action
        self.value = 0
        self.balance = 0
        self.currency = 'rub'


def find_user(_id):
    for u in users:
        if u.id == _id:
            return u


def add(_users, user):
    for u in _users:
        if u.id == user.id:
            return
    users.append(user)


def handle(user, message):
    rm = tel.ReplyKeyboardHide.create()
    answer, keyboard = handlers.handle(user, message.text)
    if keyboard:
        rm = tel.ReplyKeyboardMarkup.create(keyboard)
    if answer:
        if isinstance(answer, str):
            bot.send_message(user.id, answer, reply_markup=rm)
        else:
            bot.send_photo(user.id, answer, reply_markup=rm)
    else:
        bot.send_message(user.id, 'Я не могу понять что ты от меня хочешь', reply_markup=rm)


def main():
    current_id = None
    while True:
        updates = bot.get_updates(offset=current_id).wait() or []
        for update in updates:
            current_id = update.update_id + 1
            msg = update.message
            _user = User(msg.sender.id, '%s %s' % (msg.sender.first_name, msg.sender.last_name))
            add(users, _user)

            print '"%s" from %s' % (msg.text, _user.name)
            handle(find_user(_user.id), msg)
        if not len(updates):
            time.sleep(0.2)

main()
