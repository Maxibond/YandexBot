import json
from datetime import datetime

from users import User
from transaction import Transaction

STORAGE_USERS_FILENAME = 'users.json'
STORAGE_POOL_FILENAME = 'pool.json'


def load_users():
    try:
        with open(STORAGE_USERS_FILENAME, 'r') as f:
            data = json.load(f)
            users = [load_user(u) for u in data.get('users', [])]
            return users
    except Exception as e:
        print(e)
        return []


def load_pool():
    try:
        with open(STORAGE_POOL_FILENAME, 'r') as f:
            data = json.load(f)
            pool = {
                int(uid): [load_trans(t) for t in tx]
                for uid, tx in data.get('pool', {}).items()
            }
            return pool
    except Exception as e:
        print(e)
        return {}


def save_users(users):
    data = {
        'users': users,

    }
    with open(STORAGE_USERS_FILENAME, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_pool(pool):
    data = {
        'pool': {
            uid: [build_trans(t) for t in tx
                  if t.tag != '$yhg']
            for uid, tx in pool.items()
        }
    }
    with open(STORAGE_POOL_FILENAME, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_user(u):
    return {
        'id': u.id,
        'balance': u.balance,
        'balance_trans': build_trans(u.balance_trans),
        'name': u.name,
        'action': u.action,
        'value': u.value,
        'currency': u.currency
    }


def build_trans(t: Transaction):
    return {
        'uid': t.uid,
        'tag': t.tag,
        'data': t.data.timestamp(),
        'value': t.value
    }


def load_user(u):
    user = User(u['id'], u['name'])
    user.balance = u['balance']
    user.balance_trans = load_trans(u['balance_trans'])
    user.action = u['action']
    user.value = u['value']
    user.currency = u['currency']
    return user


def load_trans(t):
    return Transaction(t['uid'], t['tag'], datetime.fromtimestamp(t['data']), t['value'])
