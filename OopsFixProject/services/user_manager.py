import os
import json
from users.free_user import FreeUser
from users.paid_user import PaidUser

DATA_DIR = 'data/users'

def save_user(user):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{user.username}.json")
    with open(path, 'w') as f:
        json.dump({
            'username': user.username,
            'user_type': user.user_type,
            'tokens': getattr(user, 'tokens', 0),
            'text_history': user.text_history,
            'corrections': user.corrections,
            'saved_texts': getattr(user, 'saved_texts', []),
            'whitelist': getattr(user, 'whitelist', []),
            'last_login_time': getattr(user, 'last_login_time', 0),
            'password': getattr(user, 'password', None)
        }, f, indent=2)

def load_user(username):
    path = os.path.join(DATA_DIR, f"{username}.json")
    if not os.path.exists(path):
        return None

    with open(path, 'r') as f:
        data = json.load(f)

    if data['user_type'] == 'paid':
        user = PaidUser(data['username'])
        user.tokens = data.get('tokens', 0)
        user.saved_texts = data.get('saved_texts', [])
    elif data['user_type'] == 'super':
        from users.super_user import SuperUser
        user = SuperUser(data['username'])
    else:
        user = FreeUser(data['username'])

    user.text_history = data.get('text_history', [])
    user.corrections = data.get('corrections', [])
    user.whitelist = data.get("whitelist", [])
    user.last_login_time = data.get('last_login_time', 0)
    user.password = data.get("password", None)

    return user