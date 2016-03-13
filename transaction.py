# coding=utf-8
import datetime


class Transaction(object):
    def __init__(self, uid, tag, data, value):
        self.uid = uid
        self.tag = tag
        self.data = data
        self.value = value

    def __str__(self):
        return "%s %s %d" % (str(self.data)[0:-6], self.tag, self.value)


def show(user):
    res = {}
    for record in pool:
        if record.uid == user.id:
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
        if record.uid == user.id:
            i += 1
            answer = '%s\n%s' % (record, answer)
            if i == k:
                break

    return 'Последние %d транзакций - \n%s' % (i, answer)

pool = list()
pool.append(Transaction(108478453, "Еда", datetime.datetime.now(), 150))
pool.append(Transaction(108478453, "Такси", datetime.datetime.now(), 90))
pool.append(Transaction(108478453, "Молочко", datetime.datetime.now(), 50))
pool.append(Transaction(108478453, "Ананас", datetime.datetime.now(), 700))
pool.append(Transaction(108478453, "Бензин", datetime.datetime.now(), 1000))
pool.append(Transaction(108478453, "Желтая крыша", datetime.datetime.now(), 200))


