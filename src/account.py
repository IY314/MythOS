import json
import hashlib
from utils import clearterm, callterm


def init(filename='mythos/account_data.json'):
    with open(filename, 'w+') as f:
        json.dump({'current': -1, 'all': []}, f, indent=4)


def select_account(data, term, account_idx):
    if account_idx is None:
        account_idx = 0 if data.get('all') else -1
    while True:
        clearterm(term)
        callterm(term.move_y(term.height // 4), term.center('Select Account'),
                 newline=True)
        for i, a in enumerate(data['all']):
            if account_idx == i:
                callterm(term.black_on_white, a['username'],
                         term.normal, newline=True)
            else:
                print(a['username'])
        if account_idx == -1:
            callterm(term.black_on_white, 'Create new account...',
                     term.normal, newline=True)
        else:
            print('Create new account...')
        key = term.inkey()
        if key.code == term.KEY_DOWN and -1 < account_idx < len(data['all']):
            account_idx += 1
            if account_idx == len(data['all']):
                account_idx = -1
        elif key.code == term.KEY_UP \
                and (account_idx > 0 or account_idx == -1):
            account_idx -= 1
            if account_idx < 0:
                account_idx = len(data['all']) - 1
        elif key.code == term.KEY_ENTER:
            return account_idx


def login(account_idx, data, term, filename, incorrect=False):
    clearterm(term)
    account = data['all'][account_idx]
    password = account['password']
    user_input = ''
    print(f'Hi, {account["username"]}')
    if incorrect:
        print('Incorrect password')
    callterm('Enter your password: ', flush=True)

    while (key := term.inkey()).code != term.KEY_ENTER:
        if not key.is_sequence:
            user_input += key
        elif key.code == term.KEY_ESCAPE:
            return -2

    password_attempt = hashlib.sha256(user_input.encode('utf-8')).hexdigest()
    if password_attempt == password:
        data['current'] = account_idx
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        return 0
    return login(account_idx, data, term, filename, True)


def get_username(data, term):
    username = ''
    callterm('Enter a username: ', flush=True)
    while (key := term.inkey()).code != term.KEY_ENTER:
        if not key.is_sequence:
            username += key
            callterm(key, flush=True)
        elif key.code == term.KEY_BACKSPACE:
            username = username[:-1]
            callterm('\x08')
        elif key.code == term.KEY_ESCAPE:
            return -1

    if username in (a['username'] for a in data['all']):
        print('\nThat username is taken.')
        return get_username(data, term)

    print()
    return username


def get_password(term):
    password = ''
    result = ''
    prompt = 'Enter a password: '

    callterm(prompt, flush=True)
    while (key := term.inkey()).code != term.KEY_ENTER:
        if not key.is_sequence:
            password += key
            result += '*'
        elif key.code == term.KEY_BACKSPACE:
            password = password[:-1]
            result = result[:-1]
        elif key.code == term.KEY_ESCAPE:
            return -1
        clearterm(term, 'line', term.get_location())
        callterm(prompt, result, flush=True)

    print()
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def create_new_account(data, term, filename):
    while True:
        clearterm(term)

        if (username := get_username(data, term)) == -1:
            return -1

        if (password := get_password(term)) == -1:
            continue

        user = {'username': username, 'password': password}
        data['current'] = len(data['all'])
        data['all'].append(user)

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

        return 0
