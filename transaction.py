# coding=utf-8
import datetime
from collections import defaultdict


class Transaction:
    def __init__(self, uid, tag, data, value):
        self.uid = uid
        self.tag = tag
        self.data = data
        self.value = value

    def __str__(self):
        return "%s %s %d" % (str(self.data)[0:-10], self.tag, -self.value)


def show(user):
    res = {}
    for record in pool.get(user.id, []):
        if record.tag != '$yhg':
            if res.get(record.tag, False):
                res[record.tag] += record.value
            else:
                res[record.tag] = record.value
    return res


def get_tags(user):
    return [i.tag for i in pool.get(user.id, [])]


def get_history(user, k=10):
    answer = '\n'
    i = 0
    for record in pool.get(user.id, []):
        if record.tag != '$yhg':
            i += 1
            answer = '%s\n%s' % (record, answer)
            if i == k:
                break
    if i == 0:
        return "Транзакции не найдены"
    else:
        return 'Последние %d транзакций - \n%s' % (i, answer)


def cancel_last_transaction(user):
    del pool.get(user.id, [])[-1]


pool = defaultdict(list)


def fill(user):
    pool[user.id] = [Transaction(user.id, "Еда", datetime.datetime.now(), 150),
                     Transaction(user.id, "Такси", datetime.datetime.now(), 90),
                     Transaction(user.id, "Интернет", datetime.datetime.now(), 400),
                     Transaction(user.id, "Ананас", datetime.datetime.now(), 700),
                     Transaction(user.id, "Бензин", datetime.datetime.now(), 1000),
                     Transaction(user.id, "Телефон", datetime.datetime.now(), 200),
                     Transaction(user.id, "Лекарства", datetime.datetime.now(), 320),
                     Transaction(user.id, "➕Доход", datetime.datetime.now(), -3200)]
    user.balance = -sum(t.value for t in pool[user.id])
