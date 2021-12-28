from dataclasses import dataclass
from enum import IntEnum, Enum, auto
import importlib
import time
import json
from blessed import Terminal
import os

from account import (select_account,
                     login,
                     create_new_account,
                     init)
from terminal import terminal
from utils import callterm


PATHS = [
    'mythos.root.exe',
]

MAX_PASSWORD_ATTEMPTS = 4


class MythOSFileAccessMode(IntEnum):
    PRIVATE = 0b0000
    READ = 0b0001
    WRITE = 0b0010
    DELETE = 0b0100


def get_permissions_integer(*permissions):
    """

    Args:
        *permissions: the list of permissions

    Returns:
        the bitwise OR of the permission ids
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
    def __init__(self, term):
        self.term = term
        self.dirpath = ['root']

    def builtin_cd(self, *args):
        if not len(args):
            return self.log(MythOSLogLevel.ERROR, "not a directory: ''")
        path = args[0]
        if len(args) > 1:
            self.log(MythOSLogLevel.WARN,
                     f'Arguments after {path!r} are ignored')

        path_list = path.split('/')
        for i, folder in enumerate(path_list):
            if folder == '.':
                continue
            elif folder == '..' and len(self.dirpath) > 1:
                self.dirpath.pop()
            elif folder == 'root' and i == 0:
                self.dirpath.clear()
                self.dirpath.append('root')
            elif folder in os.listdir(f"mythos/{'/'.join(self.dirpath)}"):
                self.dirpath.append(folder)
            else:
                return self.log(MythOSLogLevel.ERROR,
                                f'not a directory: {folder!r}')

    def builtin_ls(self, *args):
        if len(args) > 1:
            self.log(MythOSLogLevel.WARN,
                     f'Arguments after {args[0]!r} are ignored')

        dirname = args[0] if len(args) else self.dirpath
        if os.path.isdir('/'.join(dirname)):
            for d in os.listdir(dirname):
                if os.path.isdir(os.path.join(dirname, d)):
                    callterm(self.term.turquoise1, d,
                             self.term.normal, newline=True)
                else:
                    print(d)

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


def boot(filename='mythos/account_data.json'):
    with open(filename) as f:
        data = json.load(f)

    term = Terminal()
    with term.cbreak(), term.fullscreen():
        account_idx = None
        while True:
            if data.get('current') != -1 and account_idx != -1:
                account_idx = data['current']
            else:
                account_idx = select_account(data, term, account_idx)
            if account_idx == -1:
                status = create_new_account(data, term, filename)
            else:
                status = login(account_idx, data, term, filename)
                if status == -2:
                    account_idx = -1
                    continue

            if status == -1:
                continue

            break

        terminal(term, MythOSInstance(term))


if __name__ == '__main__':
    if not os.path.exists('./mythos/account_data.json'):
        init()
    boot()
