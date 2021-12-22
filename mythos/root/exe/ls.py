from typing import Type
from mythos import MythOSInstance


def main(*args: str, instance: MythOSInstance):
    if len(args) > 1:
        instance.log(1, f'Arguments after {args[0]!r} are ignored')
