"""Account management."""

import json
import hashlib
from utils import clearterm, callterm
import utils


def init(filename='mythos/account_data.json'):
    """
    Initialize MythOS if it has not been run before.

    Args:
        filename: the filename to use for the account data

    Returns:
        None
    """
    with open(filename, 'w+') as f:
        json.dump({'current': -1, 'all': []}, f, indent=4)


def select_account(data, term, account_idx):
    """
    Display a picker to pick an account to use, and get user input.

    Args:
        data: the account data
        term: the terminal
        account_idx: the index of the account to start with

    Returns:
        The index of the account to use, or -1 if the user wants to create a
        new account
    """
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
    """
    Log in to an account.

    Args:
        account_idx: the index of the account to log in to
        data: the account data
        term: the terminal
        filename: the filename to use for the account data
        incorrect: whether the user has already entered the password
                   incorrectly

    Returns:
        The status of the login
    """
    clearterm(term)
    account = data['all'][account_idx]
    password = account['password']
    user_input = ''
    print(f'Hi, {account["username"]}')
    if incorrect:
        print('Incorrect password')
    callterm('Enter your password: ')

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
    """
    Get a username from the user.

    Args:
        data: the account data
        term: the terminal

    Returns:
        The username, or -1 if the user wants to cancel
    """

    def condition(user_input):
        if user_input in (u['username'] for u in data['all']):
            return 'That username already exists.'

    return utils.get_input(
        term,
        'Enter a username: ',
        condition=condition
    )


def get_password(term):
    """
    Get a password from the user.

    Args:
        term: the terminal

    Returns:
        The password, or -1 if the user wants to cancel
    """

    def condition(user_input):
        if len(user_input) < 8:
            return 'Password must be at least 8 characters long.'
        elif user_input.isalnum():
            return ('Password must contain at least '
                    'one non-alphanumeric character.')

    def hash_input(user_input):
        return hashlib.sha256(user_input.encode('utf-8')).hexdigest()

    return utils.get_input(
        term,
        'Enter a password: ',
        hide=True,
        condition=condition,
        hook=hash_input
    )


def create_new_account(data, term, filename):
    """
    Create a new account.

    Args:
        data: the account data
        term: the terminal
        filename: the filename to use for the account data

    Returns:
        The status of the creation
    """
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
