# coding=utf-8
import datetime
import twx.botapi as tel
import graphics
import keyboard as kb
import transaction as journal


def get_number(text):
    result = False
    try:
        result = float(text)
        result = int(text)
    finally:
        return result


class ACTION(object):
    Empty = 0
    Spend = 1
    Balance = 2
    Currency = 3
    New = 4
    values = {
        Empty: 'Action is empty',
        Spend: 'When user spend some money',
        Balance: 'When user set new balance',
        Currency: 'Users currency',
        New: 'Special action for new user',
    }


def handle_empty(user, text):
    answer = False
    keyboard = False
    if text is None:
        return "Sorry, I know only words and commands.", False
    if text.startswith('/'):
        if text == '/start':
            answer = 'Привет, %s!\n\n' \
                     'Я создан что бы помочь тебе следить за твоим расходами\n' \
                     'Давай начнем с простого - \n\n' \
                     'Сколько у тебя сейчас денег?' % user.name.encode("utf8")
            user.action = ACTION.Balance
        elif text == '/show':
            journal.show(user)
            graphics.create_png(journal.show(user))
            file_info = tel.InputFileInfo("1.png", open("1.png", "rb"), "image/png")

            return tel.InputFile("photo", file_info), False

    else:
        value = get_number(text)
        print value
        if value:
            answer = 'Напиши на что ты потратил %d %s' % (value, user.currency.encode("utf8"))
            keyboard = kb.create_keyboard(journal.get_tags(user))
            user.action = ACTION.Spend
            user.value = value
            # user.summary += value
    return answer, keyboard


def handle_spend(user, text):
    journal.pool.append(journal.Transaction(user.id, text, datetime.datetime.now(), user.value))
    user.action = ACTION.Empty
    return "Ok", False


def handle_unknown(user, text):
    return 'Haha, this is prototype!', False


def handle_balance(user, text):
    value = get_number(text)
    if value:
        user.balance = value
        user.action = ACTION.Currency
        answer = "Отлично\nТеперь укажи валюту"
        return answer, [['руб', '$', '€'], ['БЕЛЛОРУСКИЕ РУБЛИ']]
    else:
        return "Извини, но я не понимаю такое число\n" \
               "Вводи числа в формате, как показано ниже - \n\n" \
               "123\n123 00\n123.00\n\nИ так, повторим\nКакой баланс у тебя сейчас?" \
               "", False


def handle_currency(user, text):
    user.currency = text
    user.action = ACTION.Empty
    return 'Здорово\nТеперь твой баланс %d %s\n\n' \
           'А теперь давай потратим на что-нибудь деньги\n' \
           'Напиши сумму, которую ты потратил(или заработал)' \
           % (user.balance, user.currency.encode("utf8")), False


action_handler = {
    ACTION.Empty: handle_empty,
    ACTION.Spend: handle_spend,
    ACTION.Balance: handle_balance,
    ACTION.Currency: handle_currency,
    ACTION.New: handle_empty,
}


def handle(user, text):
    return action_handler[user.action](user, text)

    # if user.action == ACTION.Empty:
    #     answer, keyboard = handle_empty(user, text)
    #
    # elif user.action == ACTION.Spend:
    #     if user.trans.get(text, False):
    #         user.trans[text] += user.value
    #     else:
    #         user.trans[text] = user.value
    #     user.action = ACTION.Empty
    #     answer = 'Ok'
    # elif user.action == ACTION.Balance:
    #     user.balance = text
    #     answer = 'Ok'
    #     user.action = ACTION.Empty
    # elif user.action == ACTION.Currency:
    #     user.currency = text
    #     answer = 'Ok'
    # keyboard = kb.create_keyboard(['hello', 'Длинное слово', 'Мазик', 'а',
    #                             'проездной', 'еда', 'хз что еще', 'кальян', 'тригонометрия'])
    # print keyboard

    # answer = 'This is all your spending - \n\n'
    # print user.trans
    # for key in user.trans:
    #     answer += '\n%s - %d %s\n' % (key, round(user.trans[key]), user.currency)
    #     answer += str('|' * int(30 * user.trans[key] / user.summary)).ljust(40)
    #     answer += '%d'.rjust(4) % int(100 * user.trans[key]/user.summary) + '%'
    #     answer += '\n' + '_' * 30

    # elif text == '/setBalance':
    #     answer = 'Enter your current balance'
    #     user.action = ACTION.Balance
    # elif text == '/setCur':
    #     answer = 'Enter your currency'
    #     user.action = ACTION.Currency
