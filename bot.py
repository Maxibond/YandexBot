# coding=utf-8
import time
import twx.botapi as tel

token = '184993535:AAGdIgccMjPGHrXSjStqqJAf8eSyeEYnTas'
my_id = '108478453'
max_id = '70883634'
oleg_id = '93987418'
bot = tel.TelegramBot(token, request_method=tel.RequestMethod.GET)
bot.update_bot_info().wait()
print "Bot %s started\n" % bot.first_name
users = []
user_ids = set()


class ACTION(object):
    Empty = 0
    Spend = 1
    values = {
        Empty: 'Action is empty',
        Spend: 'When user spend some money',
    }


class User(object):
    def __init__(self, _id, name, action=ACTION.Empty):
        self.id = _id
        self.name = name
        self.action = action
        self.trans = {}
        self.value = 0


def get_number(text):
    result = False
    try:
        result = float(text)
        result = int(text)
    finally:
        return result


def find_user(_id):
    for u in users:
        if u.id == _id:
            return u


def handle(user, message):
    text = message.text
    answer = 'Sorry, I\'m don\'t know what you want. ;( \n Use /help for basic information'
    keyboard = False
    if user.action == ACTION.Empty:
        if text.startswith('/'):
            if text == '/start':
                answer = 'Hello, %s!\n'
            elif text == '/show':
                answer = 'This is all your waste\n\n'
                print user.trans
                for key in user.trans:
                    answer += '%s - %f\n' % (key, user.trans[key])
        else:
            value = get_number(text)
            print value
            if value:
                answer = 'Ok, you spend %s. For what?' % value
                keyboard = [[x] for x in user.trans.keys()]
                user.action = ACTION.Spend
                user.value = value
            pass

            if message.text in (u'Говно',):
                answer = u'Сам говно!'
    elif user.action == ACTION.Spend:
        if user.trans.get(message.text, False):
            user.trans[message.text] += user.value
        else:
            user.trans[message.text] = user.value
        user.action = ACTION.Empty

    if keyboard:
        rm = tel.ReplyKeyboardMarkup.create(keyboard)
        bot.send_message(user.id, answer, reply_markup=rm)
    else:
        bot.send_message(user.id, answer)


def main():
    current_id = None
    while True:
        updates = bot.get_updates(offset=current_id).wait()

        print "updates for bot - %s" % len(updates)
        for update in updates:
            msg = update.message
            _user = User(msg.sender.id, '%s %s' % (msg.sender.first_name, msg.sender.last_name))
            current_id = update.update_id + 1
            if _user.id not in user_ids:
                users.append(_user)
                user_ids.add(_user.id)

            handle(find_user(_user.id), msg)
            print '"%s" from %s' % (msg.text, _user.name)
        time.sleep(2)


main()

# keyboard = [
#     ['Oleg', 'Oleg'],
#     ['Oleg', 'Oleg'],
# ]
