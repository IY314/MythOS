"""Main file for MythOS."""

import importlib
import json
import os
import time
from dataclasses import dataclass
from enum import IntEnum, Enum, auto
import sys

from blessed import Terminal

from account import (select_account,
                     login,
                     create_new_account,
                     init)
from terminal import terminal
from utils import callterm, ExecExit


sys.path.append('.')


PATHS = [
    'mythos.root.exe',
]

MAX_PASSWORD_ATTEMPTS = 4


class MythOSFileAccessMode(IntEnum):
    """Enum for file access modes."""

    PRIVATE = 0b0000
    READ = 0b0001
    WRITE = 0b0010
    DELETE = 0b0100


def get_permissions_integer(*permissions):
    """
    Get an integer representing permissions for a file.

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
    """Enum for return status codes."""

    SUCCESS = 200
    UNAUTHORIZED = 401
    ACCESS_DENIED = 403
    NOT_FOUND = 404


class MythOSUserRank(Enum):
    """Enum for user rank levels."""

    USER = auto()
    ADMIN = auto()
    OWNER = auto()


class MythOSPermission:
    """A permission for a file."""

    DEFAULT_USER_PERM = 'READ',
    DEFAULT_ADMIN_PERM = 'READ', 'WRITE', 'DELETE'
    DEFAULT_OWNER_PERM = 'READ', 'WRITE', 'DELETE'

    def __init__(self, *, user=None, admin=None, owner=None):
        """Create a new file permission object."""
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
        """Get the permission for a user rank."""
        if isinstance(index, MythOSUserRank):
            return getattr(self, index.name.lower())
        elif isinstance(index, str):
            return getattr(self, index.lower())
        else:
            raise TypeError(f'invalid index type {type(index)}')


@dataclass
class MythOSUser:
    """A user account."""

    username: str
    password: str
    rank: MythOSUserRank


class MythOSLogLevel(Enum):
    """Enum for logging levels."""

    INFO = auto()
    WARN = auto()
    ERROR = auto()
    FATAL = auto()


def argc_check(*, lower=0, upper=1):
    """
    Check the number of arguments for a command.

    Args:
        lower: the lower bound of the number of arguments
        upper: the upper bound of the number of arguments

    Returns:
        A function wrapper that checks the number of arguments before executing
    """
    def decorator(func):
        def wrapper(self, *args):
            if len(args) < lower:
                self.log(MythOSLogLevel.WARN,
                         f'Too few arguments (expected at least {lower})')
            elif len(args) > upper:
                self.log(
                    MythOSLogLevel.WARN,
                    f'Arguments after {args[upper - 1]!r} will be ignored'
                )
            return func(self, *args)
        return wrapper
    return decorator


class MythOSInstance:
    """An instance of a MythOS process."""

    def __init__(self, term: Terminal) -> None:
        """Initialize a new MythOS instance."""
        self.term = term
        self.dirpath = ['root']
        self.paths = [['exe']]

    @argc_check()
    def builtin_cd(self, *args):
        """
        Change the current working directory.

        Args:
            *args: the args passed to the command

        Returns:
            None
        """
        if not len(args):
            return self.log(MythOSLogLevel.ERROR, "not a directory: ''")
        path = args[0]

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

    @argc_check()
    def builtin_ls(self, *args):
        """
        List the contents of the current directory or a specified directory.

        Args:
            *args: the args passed to the command

        Returns:
            None
        """
        current_dir = self.dirpath[1:] if len(self.dirpath) - 1 else []

        dirname = 'mythos/root/' + \
            (args[0] if len(args) else '/'.join(current_dir))
        if os.path.isdir(dirname):
            for d in os.listdir(dirname):
                if os.path.isdir(os.path.join(dirname, d)):
                    callterm(self.term.turquoise1, d,
                             self.term.normal, newline=True)
                else:
                    print(d)
        else:
            return self.log(MythOSLogLevel.ERROR,
                            f'not a directory: {dirname}')

    @argc_check(upper=0)
    def builtin_exit(self, *_):
        """
        Exit the MythOS shell.

        Args:
            *_: the args passed to the command (ignored)

        Returns:
            None
        """
        exit(0)

    def run_file(self, path, *args):
        """
        Run a specified file.

        Args:
            path: the path to the file
            *args: the args passed to the file

        Returns:
            None
        """
        if path[0]:
            module = importlib.import_module(
                'mythos.' + ('.'.join(path[1:])))
            try:
                module.run(*args)
            except ExecExit:
                pass

    def log(self, level, details):
        """
        Log a message to the console.

        Args:
            level: the level of the message
            details: the details of the message

        Returns:
            None
        """
        if isinstance(level, int):
            level = MythOSLogLevel(level + 1)
        print(f'{time.strftime("%H:%M:%S")} [{level.name}]: {details}')


@dataclass
class MythOSFile:
    """A file in the MythOS filesystem."""

    name: str
    extension: str
    permission: MythOSPermission

    def open(self, user, args, modes):
        """
        Run a file.

        Args:
            user: the user running the file
            args: the arguments passed to the file
            modes: the modes of running the file

        Returns:
            None
        """
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
    """
    Boot MythOS.

    Args:
        filename: the filename of the account data file

    Returns:
        None
    """
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
