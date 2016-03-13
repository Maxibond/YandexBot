# coding=utf-8
import datetime
import twx.botapi as tel
import draw
import keyboard as kb
import transaction as journal


def get_number(text, user):
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

slovar = {
    '/start': ['старт', 'обучение', 'помощь', '/start'],
    '/setbalance': ['баланс', 'установить', '/setbalance'],
    '/total': ['всего', 'стат', 'месяц', '/total'],
    '/history': ['история', 'напомни', '/history'],
}


def handle_empty(user, text):
    answer, keyboard = False, False
    if text is None:
        return "Я могу отвечать только на текст.", False
    if text.startswith('/'):
        if text.startswith('/start'):
            answer = 'Привет, %s!\n\n' \
                     'Я создан что бы помочь тебе следить за твоим расходами\n' \
                     'Давай начнем с простого - \n\n' \
                     'Сколько у тебя сейчас денег?' % user.name.encode("utf8")
            user.action = ACTION.Balance
            action_handler[ACTION.Spend] = t_handle_spend
            action_handler[ACTION.Balance] = t_handle_balance
            action_handler[ACTION.Currency] = t_handle_currency
        elif text.startswith('/total'):
            records = journal.show(user)
            if len(records):
                draw.drawCircle(u"Март", records)
                file_info = tel.InputFileInfo("1.png", open("1.png", "rb"), "image/png")
                return tel.InputFile("photo", file_info), False
            else:
                return "Слишком мало данных для статистики", False
        elif text.startswith('/balance'):
            answer = 'Текущий баланс - %d%s\n' % (user.balance, user.currency)
        elif text.startswith('/setbalance'):
            user.action = ACTION.Balance
            answer = 'Текущий баланс - %d%s.\n/setbalance для отмены.\nВведите новое значение - ' \
                     % (user.balance, user.currency.encode('utf8'))
        elif text.startswith('/history'):
            answer = journal.get_history(user)
            return answer, False
    else:
        value = get_number(text, user)
        print value
        if not value:
            text = text.split(' ')
            if len(text) == 2:
                value = get_number(text[0], user)
                answer = text[1]
                if not value:
                    value = get_number(text[1], user)
                    answer = text[0]
        if not answer:
            answer = 'На что ты потратил %d%s?' % (value, user)
        if value:
            keyboard = kb.create_keyboard(journal.get_tags(user))
            user.action = ACTION.Spend
            user.value = value
    return answer, keyboard


def handle_spend(user, text):
    if text == "Прибыль":
        user.value = -user.value
    journal.pool.append(journal.Transaction(user.id, text, datetime.datetime.now(), user.value))
    user.balance -= user.value
    user.action = ACTION.Empty
    return "Ok", False


def handle_balance(user, text):
    if text.startswith('/setbalance'):
        user.action = ACTION.Empty
        return "Отменено", False
    value = get_number(text, user)
    if value:
        user.balance = value
        user.action = ACTION.Empty
        answer = "Новый баланс сохранен"
        return answer, False
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


def t_handle_spend(user, text):
    if text == "Прибыль":
        user.value = -user.value
    journal.pool.append(journal.Transaction(user.id, text, datetime.datetime.now(), user.value))
    user.action = ACTION.Empty
    user.balance -= user.value
    action_handler[ACTION.Spend] = handle_spend
    return ('%d' % user.value), False
    # return ('%d%s%sn%d%s' % (user.value, user.currency, text, user.balance, user.currency)), False


def t_handle_balance(user, text):
    value = get_number(text, user)
    if value:
        user.balance = value
        user.action = ACTION.Currency
        answer = "Отлично!\nТеперь укажи валюту"
        action_handler[ACTION.Balance] = handle_balance
        return answer, [['руб'], ['$'], ['€'], ]
    else:
        return "Извини, но я не понимаю такое число\n" \
              "Вводи числа в формате, как показано ниже - \n\n" \
              "123\n123\n123.00\n\nИ так, повторим\nКакой баланс у тебя сейчас?", False


def t_handle_currency(user, text):
    user.currency = text
    user.action = ACTION.Empty
    action_handler[ACTION.Currency] = handle_currency
    return 'Здорово\nТеперь твой баланс %d%s\n\n' \
        'А теперь давай потратим на что-нибудь деньги\n' \
        'Напиши сумму, которую ты потратил(или заработал)' \
        % (user.balance, user.currency.encode("utf8")), False


action_handler = {
    ACTION.Empty: handle_empty,
    ACTION.Spend: handle_spend,
    ACTION.Balance: handle_balance,
    ACTION.Currency: handle_currency,
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
