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
    AskingTutorial = 20
    TutorialSpend = 21
    TutorialBalance = 22
    TutorialCurrency = 23
    values = {
        Empty: 'Action is empty',
        Spend: 'When user spend some money',
        Balance: 'When user set new balance',
        Currency: 'Users currency',
        AskingTutorial: 'Asking tutorial',
    }


synonym = {
    '/start': ['Cтарт', 'Начать', 'start'],
    '/setbalance': ['Изменить баланс', 'setbalance'],
    '/total': ['Всего', 'Статистика', 'Месяц', 'total'],
    '/history': ['История', 'Выписка', 'history'],
    '/balance': ['balance', 'Баланс', 'Остаток'],
    '/stats': ['stats', 'Статистика'],
    '/cancel': ['Отмена', 'cancel'],
    '/tutorial': ['Обучение', 'tutorial'],
    '/help': ['help', 'Помощь', 'Хелп'],
}


def is_command(text, command):
    return text.startswith(command) or text.lower() in synonym.get(command, [])


def handle_empty(user, text: str):
    answer, keyboard = False, False
    if text is None:
        return "Я могу отвечать только на текст.", False

    elif is_command(text, '/start'):
        answer = 'Привет! Я снова живу!\n\n' \
                 '/help для списка команд\n' \
                 'Я создан что бы помочь тебе следить за твоими средствами.\n' \
                 f'Хочешь начать с обучения, {user.name}?'
        user.action = ACTION.AskingTutorial
        return answer, kb.create_keyboard('Да', 'Нет')
    elif is_command(text, '/tutorial'):
        return handle_tutorial(user, text)
    elif is_command(text, '/total'):
        records = journal.show(user)
        if len(records):
            filename = f"{IMAGE_PATH}/{user.id}-total.png"
            draw.drawCircle(filename, datetime.datetime.now().strftime("%B"), records)
            file_info = tel.InputFileInfo(filename, open(filename, "rb"), "image/png")
            return tel.InputFile("photo", file_info), False
        else:
            return "Слишком мало данных для статистики", False
    elif is_command(text, '/balance'):
        answer = 'Текущий баланс %d%s\n' % (user.balance, user.currency)

    elif is_command(text, '/setbalance'):
        user.action = ACTION.Balance
        answer = 'Текущий баланс - %d%s.\n/setbalance для отмены.\nВведите новое значение - ' \
                 % (user.balance, user.currency)
    elif is_command(text, '/history'):
        answer = journal.get_history(user)
        return answer, False
    elif is_command(text, '/stats'):
        records = journal.show(user)
        if len(records):
            filename = f"{IMAGE_PATH}/{user.id}-stats.png"
            draw.drawLines(filename, datetime.datetime.now().strftime("%B"), records)
            file_info = tel.InputFileInfo(filename, open(filename, "rb"), "image/png")
            return tel.InputFile("photo", file_info), False
        else:
            return "Слишком мало данных для статистики", False
    elif is_command(text, '/cancel'):
        user.action = ACTION.Empty
        journal.cancel_last_transaction(user)
        return "Последняя транзакция отменена.", False
    elif is_command(text, '/help'):
        return '''
        Введите любое число, чтобы начать транзакцию.
        /start - начни обучение здесь
        /setbalance - установить баланс
        /total - показать суммарный баланс за месяц
        /history - показать историю транзакций
        /balance - проверить баланс
        /stats - показать статистику за месяц
        /cancel - отмена операции
        /tutorial - начать обучение
        /help - подсказка
        /f - [debug] установить демо транзакции (стирает ваши транзакции, осторожно!)
        ''', False
    elif is_command(text, '/f'):
        journal.fill(user)
        answer = "Готово"
    else:
        value = get_number(text, user)
        if value < 0 or value > VERY_BIG_NUMBER:
            return "Введите положительное разумное число!", False

        if value:
            answer = 'На что ты потратил %d%s?\nЕсли это заработанные средства - Жми "➕Доход"' % (value, user.currency)
            keyboard = kb.create_keyboard_with_tags(journal.get_tags(user))
            user.action = ACTION.Spend
            user.value = value
    return answer, keyboard


def handle_spend(user, text):
    if text == "➕Доход":
        user.value = -user.value
    journal.pool.get(user.id, []).append(journal.Transaction(user.id, text, datetime.datetime.now(), user.value))
    user.balance -= user.value
    user.action = ACTION.Empty
    if user.value > 0:
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
        journal.pool.get(user.id, []).append(journal.Transaction(user.id, "➕Доход", datetime.datetime.now(), 0))
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


def handle_asking_tutorial(user, text):
    if text.lower() == 'да':
        return handle_tutorial(user, text)
    elif text.lower() == 'нет':
        user.action = ACTION.Empty
        return 'Ну ладно. Посмотри /help для ознакомления с командами', False
    return 'Я тебя не понял. Cкажи НЕТ если не хочешь :)', kb.create_keyboard('Да', 'Нет')


def handle_tutorial(user, text):
    user.action = ACTION.TutorialBalance
    return 'Давай начнём с простого! Какой у тебя текущий баланс?', False


def t_handle_spend(user, text):
    user.action = ACTION.Empty
    if is_command(text, '/cancel'):
        return 'Обучение закончено!', False
    if text == "➕Доход":
        user.value = -user
    journal.pool.get(user.id, []).append(journal.Transaction(user.id, text, datetime.datetime.now(), user.value))
    user.balance -= user.value
    if user.value >= 0:
        return f'Ты потратил {user.value} {user.currency} на {text}.\n' \
               f' Текущий баланс - {user.balance} {user.currency}', False
    else:
        return 'Текущий баланс - %d%s' % (user.balance, user.currency), False


def t_handle_balance(user, text):
    if is_command(text, '/cancel'):
        user.action = ACTION.Empty
        return 'Обучение закончено!', False

    value = get_number(text, user)
    if value < 0 or value > VERY_BIG_NUMBER:
        return "Введите положительное разумное число!", False

    if value:
        delta = value - user.balance
        user.balance_trans.value += delta
        user.balance = value
        user.action = ACTION.Empty
        answer = f'Твой баланс {user.balance} {user.currency}\n\n' \
                 f'А теперь давай потратимся на что-нибудь\n' \
                 'Напиши сумму, которую ты потратил(или заработал)'
        return answer, False
    else:
        return "Извини, но я не понимаю такое число\nВводи числа в формате, как показано ниже - " \
               "\n\n123\n123\n123.00\n\nИ так, повторим\nКакой баланс у тебя сейчас?", False


def t_handle_currency(user, text):
    if is_command(text, '/cancel'):
        user.action = ACTION.Empty
        return 'Обучение закончено!', False

    user.currency = text.replace('.', ' ').strip()
    user.action = ACTION.Empty
    return 'Твой баланс %d%s\n\nА теперь давай потратимся на что-нибудь\n' \
           'Напиши сумму, которую ты потратил(или заработал)' % (user.balance, user.currency), False


action_handler = {
    ACTION.Empty: handle_empty,
    ACTION.Spend: handle_spend,
    ACTION.Balance: handle_balance,
    # ACTION.Currency: handle_currency,
    ACTION.AskingTutorial: handle_asking_tutorial,
    ACTION.TutorialSpend: t_handle_spend,
    ACTION.TutorialBalance: t_handle_balance,
    # ACTION.TutorialCurrency: t_handle_currency,
}


def handle(user, text):
    return action_handler[user.action](user, text)
