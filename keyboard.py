# coding=utf-8
def sort_by_size(keys):
    is_done = False
    while not is_done:
        is_done = True
        for i in range(len(keys)-1):
            if len(keys[i]) > len(keys[i+1]):
                is_done = False
                keys[i], keys[i+1] = keys[i+1], keys[i]


def free_len(k):
    res = 0
    for i in k:
        if res < len(i) + 2:
            res = len(i) + 2
    return 50 - res*len(k)


def add_button(kb, key):
    if not kb:
        kb.append([key])
    else:
        for k in kb:
            if len(key) < free_len(k):
                k.append(key)
                return
        kb.append([key])


def create_keyboard(keys):
    sort_by_size(keys)
    if 'Прибыль' in keys:
        keys.remove('Прибыль')
    if '$yhg' in keys:
        keys.remove('$yhg')
    kb = [['Прибыль'], ]
    for key in keys:
        add_button(kb, key)
    return kb
