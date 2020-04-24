# coding=utf-8
import datetime
import time

import twx.botapi as tel
import draw
import keyboard as kb
import transaction as journal


VERY_BIG_NUMBER = 9_876_543
IMAGE_PATH = './images'


def get_number(text, user):
    if text == '0':
        return 0
    text = text.replace(user.currency, ' ').strip()
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
    values = {
        Empty: 'Action is empty',
        Spend: 'When user spend some money',
        Balance: 'When user set new balance',
        Currency: 'Users currency',
    }

synonym = {
    '/start': ['Cтарт', 'Обучение', 'Помощь', '/start'],
    '/setbalance': ['Изменить баланс', '/setbalance'],
    '/total': ['Всего', 'Статистика', 'Месяц', '/total'],
    '/history': ['История', 'Выписка', '/history'],
    '/balance': ['/balance', 'Баланс', 'Остаток'],
    '/stats': ['/stats', 'Статистика'],
    '/cancel': ['Отмена', '/cancel'],
}


def handle_empty(user, text: str):
    answer, keyboard = False, False
    if text is None:
        return "Я могу отвечать только на текст.", False

    elif text.lower() in synonym['/start'] or text.startswith('/start'):
        answer = 'Привет, %s!\n\n' \
                 'Я создан что бы помочь тебе следить за твоими средствами.\n' \
                 'Давай начнем с простого. \n\n' \
                 'Задай текущий баланс' % user.name
        user.action = ACTION.Balance
        action_handler[ACTION.Spend] = t_handle_spend
        action_handler[ACTION.Balance] = t_handle_balance
        action_handler[ACTION.Currency] = t_handle_currency
    elif text.lower() in synonym['/total']:
        records = journal.show(user)
        if len(records):
            filename = f"{IMAGE_PATH}/{user.id}-total.png"
            draw.drawCircle(filename, datetime.datetime.now().strftime("%B"), records)
            file_info = tel.InputFileInfo(filename, open(filename, "rb"), "image/png")
            return tel.InputFile("photo", file_info), False
        else:
            return "Слишком мало данных для статистики", False
    elif text.lower().strip() in synonym['/balance']:
        answer = 'Текущий баланс %d%s\n' % (user.balance, user.currency)

    elif text.lower() in synonym['/setbalance']:
        user.action = ACTION.Balance
        answer = 'Текущий баланс - %d%s.\n/setbalance для отмены.\nВведите новое значение - ' \
                 % (user.balance, user.currency)
    elif text.lower() in synonym['/history']:
        answer = journal.get_history(user)
        return answer, False
    elif text.lower() in synonym['/stats']:
        records = journal.show(user)
        if len(records):
            filename = f"{IMAGE_PATH}/{user.id}-stats.png"
            draw.drawLines(filename, datetime.datetime.now().strftime("%B"), records)
            file_info = tel.InputFileInfo(filename, open(filename, "rb"), "image/png")
            return tel.InputFile("photo", file_info), False
        else:
            return "Слишком мало данных для статистики", False
    elif text.lower() in synonym['/cancel']:
        journal.cancel_last_transaction(user)
        return "Последняя транзакция отменена.", False
    elif text == '/f':
        journal.fill(user)
        answer = "Готово"
    else:
        value = get_number(text, user)
        if value < 0 or value > VERY_BIG_NUMBER:
            return "Введите положительное разумное число!", False

        if value:
            answer = 'На что ты потратил %d%s?\nЕсли это заработанные средства - Жми "➕Доход"' % (value, user.currency)
            keyboard = kb.create_keyboard(journal.get_tags(user))
            user.action = ACTION.Spend
            user.value = value
    return answer, keyboard


def handle_spend(user, text):
    if text == "➕Доход":
        user.value = -user.value
    journal.pool.get(user.id, []).append(journal.Transaction(user.id, text, datetime.datetime.now(), user.value))
    user.balance -= user.value
    user.action = ACTION.Empty
    if user.value >= 0:
        return 'Ты потратил %d%s на %s.\n Текущий баланс - %d%s' \
               % (user.value, user.currency, text, user.balance, user.currency), False
    else:
        return 'Текущий баланс %d%s' % (user.balance, user.currency), False


def handle_balance(user, text):
    if text.startswith('/setbalance'):
        user.action = ACTION.Empty
        return "Отменено", False
    value = get_number(text, user)
    if value < 0 or value > VERY_BIG_NUMBER:
        return "Введите положительное разумное число!", False

    if value:
        delta = value - user.balance
        user.balance = value
        journal.pool.get(user.id, []).append(journal.Transaction(user.id, "➕Доход"))
        user.balance_trans.value += delta
        user.action = ACTION.Empty
        answer = "Новый баланс - %d%s" % (user.balance, user.currency)
        return answer, False
    else:
        return "Извини, но я не понимаю такое число\nВводи числа в формате, как показано ниже -" \
               "\n\n123\n123 00\n123.00\n\nИ так, повторим\nКакой баланс у тебя сейчас?", False


def handle_currency(user, text):
    user.currency = text
    user.action = ACTION.Empty
    return 'Здорово\nТеперь твой баланс %d %s\n\n' \
           'А теперь давай потратим на что-нибудь деньги\n' \
           'Напиши сумму, которую ты потратил(или заработал)' \
           % (user.balance, user.currency), False


def t_handle_spend(user, text):
    if text == "➕Доход":
        user.value = -user.value
    journal.pool.get(user.id, []).append(journal.Transaction(user.id, text, datetime.datetime.now(), user.value))
    user.action = ACTION.Empty
    user.balance -= user.value
    action_handler[ACTION.Spend] = handle_spend
    if user.value >= 0:
        return 'Ты потратил %d%s на %s.\n Текущий баланс - %d%s' \
               % (user.value, user.currency, text, user.balance, user.currency), False
    else:
        return 'Текущий баланс - %d%s' % (user.balance, user.currency), False


def t_handle_balance(user, text):
    value = get_number(text, user)
    if value < 0 or value > VERY_BIG_NUMBER:
        return "Введите положительное разумное число!", False

    if value:
        delta = value - user.balance
        user.balance_trans.value += delta
        user.balance = value
        user.action = ACTION.Currency
        answer = "Отлично!\nТеперь укажи валюту"
        action_handler[ACTION.Balance] = handle_balance
        return answer, [['руб'], ['$'], ['€']]
    else:
        return "Извини, но я не понимаю такое число\nВводи числа в формате, как показано ниже - " \
              "\n\n123\n123\n123.00\n\nИ так, повторим\nКакой баланс у тебя сейчас?", False


def t_handle_currency(user, text):
    user.currency = text.replace('.', ' ').strip()
    user.action = ACTION.Empty
    action_handler[ACTION.Currency] = handle_currency
    return 'Твой баланс %d%s\n\nА теперь давай потратимся на что-нибудь\n' \
        'Напиши сумму, которую ты потратил(или заработал)' % (user.balance, user.currency), False


action_handler = {
    ACTION.Empty: handle_empty,
    ACTION.Spend: handle_spend,
    ACTION.Balance: handle_balance,
    ACTION.Currency: handle_currency,
}


def handle(user, text):
    return action_handler[user.action](user, text)
