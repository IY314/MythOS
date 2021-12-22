from dataclasses import dataclass
from enum import IntEnum, Enum, auto
from typing import Callable, Optional, Sequence, Text, Union
import importlib
import time


PATHS = [
    'mythos.root.exe',
]


class MythOSFileAccessMode(IntEnum):
    PRIVATE = 0b0000
    READ = 0b0001
    WRITE = 0b0010
    DELETE = 0b0100


def get_permissions_integer(*permissions: str) -> int:
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

    def __init__(self, *, user: Optional[Sequence[str]] = None,
                 admin: Optional[Sequence[str]] = None,
                 owner: Optional[Sequence[str]] = None) -> None:
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
    
    def __getitem__(self, index: MythOSUserRank) -> int:
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
    def log(self, level: Union[MythOSLogLevel, int], details: Text) -> None:
        if isinstance(level, int):
            level = MythOSLogLevel(level + 1)
        print(f'{time.strftime("%H:%M:%S")} [{level.name}]: {details}')


@dataclass
class MythOSFile:
    name: str
    extension: str
    permission: MythOSPermission

    def open(self, user: MythOSUser,
                   args: Sequence[str],
                   modes: Sequence[str]) -> MythOSReturnStatus:
        if get_permissions_integer(*modes) > self.permission[user.rank]:
            return MythOSReturnStatus.ACCESS_DENIED
        if self.extension == 'exe':
            for path in PATHS:
                try:
                    executable = importlib.import_module(self.name, path)
                    if (exec_func := getattr(executable, 'main')) is None \
                    or not isinstance(
                        exec_func, Callable[[Sequence[str]], MythOSReturnStatus]
                    ):
                        raise AttributeError('main function not found in'
                                             'module')
                    return exec_func(*args)
                except ModuleNotFoundError:
                    continue
            return MythOSReturnStatus.NOT_FOUND
