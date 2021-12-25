from dataclasses import dataclass
from enum import IntEnum, Enum, auto
import importlib
import time
import json
from blessed import Terminal
import os
import hashlib


PATHS = [
    'mythos.root.exe',
]


class MythOSFileAccessMode(IntEnum):
    PRIVATE = 0b0000
    READ = 0b0001
    WRITE = 0b0010
    DELETE = 0b0100


def get_permissions_integer(*permissions):
    """Return the permissions integer from the permissions listed.

    Raises:
        ValueError: Raised if the permission given is invalid

    Returns:
        int: The bitwise OR of all permissions listed
    """

    value = int(MythOSFileAccessMode.PRIVATE)
    for perm in permissions:
        if status := getattr(MythOSFileAccessMode, perm) is None:
            raise ValueError(f'invalid permission status {perm}')
        value |= status

    return value


class MythOSReturnStatus(Enum):
    SUCCESS = 200
    UNAUTHORIZED = 401
    ACCESS_DENIED = 403
    NOT_FOUND = 404


class MythOSUserRank(Enum):
    USER = auto()
    ADMIN = auto()
    OWNER = auto()


class MythOSPermission:
    DEFAULT_USER_PERM = 'READ',
    DEFAULT_ADMIN_PERM = 'READ', 'WRITE', 'DELETE'
    DEFAULT_OWNER_PERM = 'READ', 'WRITE', 'DELETE'

    def __init__(self, *, user=None, admin=None, owner=None):
        if user is None:
            user = self.DEFAULT_USER_PERM
        if admin is None:
            admin = self.DEFAULT_ADMIN_PERM
        if owner is None:
            owner = self.DEFAULT_OWNER_PERM
        self.user = get_permissions_integer(*user)
        self.admin = get_permissions_integer(*admin)
        self.owner = get_permissions_integer(*owner)

        assert self.owner > self.admin > self.user, \
            'Invalid permission hierarchy'

    def __getitem__(self, index):
        return getattr(self, index.name.lower())


@dataclass
class MythOSUser:
    username: str
    password: str
    rank: MythOSUserRank


class MythOSLogLevel(Enum):
    INFO = auto()
    WARN = auto()
    ERROR = auto()
    FATAL = auto()


class MythOSInstance:
    def log(self, level, details):
        if isinstance(level, int):
            level = MythOSLogLevel(level + 1)
        print(f'{time.strftime("%H:%M:%S")} [{level.name}]: {details}')


@dataclass
class MythOSFile:
    name: str
    extension: str
    permission: MythOSPermission

    def open(self, user, args, modes):
        if get_permissions_integer(*modes) > self.permission[user.rank]:
            return MythOSReturnStatus.ACCESS_DENIED
        if self.extension == 'exe':
            for path in PATHS:
                try:
                    executable = importlib.import_module(self.name, path)
                    if (exec_func := getattr(executable, 'main')) is None \
                            or not callable(exec_func):
                        raise AttributeError(
                            'main function not found in module'
                        )
                    return exec_func(*args)
                except ModuleNotFoundError:
                    continue
            return MythOSReturnStatus.NOT_FOUND


def mod_input(prompt='>', *, type_=str, retry=False):
    while True:
        try:
            return type_(input(prompt))
        except ValueError:
            if not retry:
                return None


def callterm(*calls, newline=False):
    print(*calls, sep='', end='')
    if newline:
        print()


def clearterm(term):
    callterm(term.home, term.clear, term.normal)
    callterm(term.center(' MythOS v1.0.0 ', fillchar=f'='), newline=True)
    print()


def init(filename='mythos/account_data.json'):
    with open(filename, 'w+') as f:
        json.dump({'current': None, 'all': []}, f, indent=4)


def select_account(data, term, account_idx):
    if account_idx is None:
        account_idx = 0 if data.get('all') else -1
    while True:
        clearterm(term)
        callterm(term.center('Select Account'), newline=True)
        for i, a in enumerate(data['all']):
            if account_idx == i:
                callterm(term.black_on_white, a['username'], term.normal, newline=True)
            else:
                print(a['username'])
        if account_idx == -1:
            callterm(term.black_on_white, 'Create new account...', term.normal, newline=True)
        else:
            print('Create new account...')
        key = term.inkey()
        if key.code == term.KEY_DOWN and -1 < account_idx < len(data['all']):
            account_idx += 1
            if account_idx == len(data['all']):
                account_idx = -1
        elif key.code == term.KEY_UP and (account_idx > 0 or account_idx == -1):
            account_idx -= 1
            if account_idx < 0:
                account_idx = len(data['all']) - 1
        elif key.code == term.KEY_ENTER:
            return account_idx


def login(account_idx, data, term, filename):
    clearterm(term)
    password = data['all'][account_idx]['password']
    user_input = ''
    print(f'Hi, {data["all"][account_idx]["username"]}')
    print('Enter your password')

    while (key := term.inkey()).code != term.KEY_ENTER:
        if not key.is_sequence:
            user_input += key
        elif key.code == term.KEY_ESCAPE:
            return -1
    
    password_attempt = hashlib.sha256(user_input.encode('utf-8')).hexdigest()
    if password_attempt == password:
        data['current'] = data['all'][account_idx]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        return 0
    return 1


def get_username(term):
    username = ''
    callterm('Enter a username: ')
    while (key := term.inkey()).code != term.KEY_ENTER:
        if not key.is_sequence:
            username += key
            callterm(key)
        elif key.code == term.KEY_BACKSPACE:
            username = username[:-1]
            callterm('\x08')
        elif key.code == term.KEY_ESCAPE:
            return -1
    
    return username


def get_password(term):
    password = ''

    callterm('Enter a password: ')
    while (key := term.inkey()).code != term.KEY_ENTER:
        if not key.is_sequence:
            password += key
            callterm('*')
        elif key.code == term.KEY_BACKSPACE:
            password = password[:-1]
            callterm('\x08')
        elif key.code == term.KEY_ESCAPE:
            return -1

    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def create_new_account(data, term, filename):
    while True:
        clearterm(term)

        username = get_username(term)
        if username == -1:
            return -1

        password = get_password(term)
        if password == -1:
            continue
        
        user = {'username': username, 'password': password}
        data['all'].append(user)
        data['current'] = user

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        
        return 0
        


def boot(filename='mythos/account_data.json'):
    data = None

    with open(filename) as f:
        data = json.load(f)

    term = Terminal()
    with term.cbreak(), term.fullscreen():
        account_idx = None
        while True:
            account_idx = select_account(data, term, account_idx)
            if account_idx == -1:
                status = create_new_account(data, term, filename)
            else:
                status = login(account_idx, data, term, filename)

            if status == -1:
                continue

            break

        clearterm(term)



if __name__ == '__main__':
    if not os.path.exists('./mythos/account_data.json'):
        init()
    boot()
