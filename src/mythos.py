from dataclasses import dataclass
from enum import IntEnum, Enum, auto
import importlib
import time
import json
from blessed import Terminal


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


def boot(filename='mythos/account_data.json'):
    data = None

    with open(filename) as f:
        data = json.load(f)

    term = Terminal()
    with term.cbreak(), term.fullscreen():
        while True:
            callterm(term.home, term.clear)
            callterm(term.center(' MythOS v1.0.0 ', fillchar=f'='), newline=True)
            callterm(term.center('Select Account'), newline=True)
            for a in data.get('all', []):
                pass


if __name__ == '__main__':
    boot()
