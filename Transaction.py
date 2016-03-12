# coding=utf-8
import datetime


class Transaction(object):
    def __init__(self, uid, tag, data, value):
        self.uid = uid
        self.tag = tag
        self.data = data
        self.value = value

    def __str__(self):
        return "%s %s %d" % (str(self.data), self.tag, self.value)


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

pool = list()
pool.append(Transaction(108478453, u"Молочко", datetime.datetime.now(), 50))
pool.append(Transaction(108478453, u"Еда", datetime.datetime.now(), 150))
pool.append(Transaction(108478453, u"Такси", datetime.datetime.now(), 90))
pool.append(Transaction(108478453, u"Ананас", datetime.datetime.now(), 700))
pool.append(Transaction(108478453, u"Бензин", datetime.datetime.now(), 1000))
pool.append(Transaction(108478453, u"Желтая крыша", datetime.datetime.now(), 200))


