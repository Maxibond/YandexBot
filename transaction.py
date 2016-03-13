# coding=utf-8
import datetime


class Transaction(object):
    def __init__(self, uid, tag, data, value):
        self.uid = uid
        self.tag = tag
        self.data = data
        self.value = value

    def __str__(self):
        return "%s %s %d" % (str(self.data)[0:-6], self.tag, -self.value)


def show(user):
    res = {}
    for record in pool:
        if record.uid == user.id and record.tag != '$yhg':
            if res.get(record.tag, False):
                res[record.tag] += record.value
            else:
                res[record.tag] = record.value
    return res


def get_tags(user):
    return list({i.tag for i in pool if i.uid == user.id})


def get_history(user, k=10):
    answer = '\n'
    i = 0
    for record in pool:
        if record.uid == user.id and record.tag != '$yhg':
            i += 1
            answer = '%s\n%s' % (record, answer)
            if i == k:
                break
    if i == 0:
        return "Транзакцие не найдены"
    else:
        return 'Последние %d транзакций - \n%s' % (i, answer)


def cancel_last_transaction(user):
    for i in xrange(len(pool), 0, -1):
        if pool[i].uid == user.id:
            del pool[i]


pool = list()


def fill(user):
    pool.append(Transaction(user.id, "Еда", datetime.datetime.now(), 150))
    pool.append(Transaction(user.id, "Такси", datetime.datetime.now(), 90))
    pool.append(Transaction(user.id, "Интернет", datetime.datetime.now(), 400))
    pool.append(Transaction(user.id, "Ананас", datetime.datetime.now(), 700))
    pool.append(Transaction(user.id, "Бензин", datetime.datetime.now(), 1000))
    pool.append(Transaction(user.id, "Телефон", datetime.datetime.now(), 200))
    pool.append(Transaction(user.id, "Прибыль", datetime.datetime.now(), 2000))


