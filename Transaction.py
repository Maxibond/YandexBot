# coding=utf-8
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
            print(record)
            if res.get(record.tag, False):
                res[record.tag] += record.value
            else:
                res[record.tag] = record.value
    return res


def get_tags(user):
    return list({i.tag for i in pool if i.uid == user.id})

pool = list()


