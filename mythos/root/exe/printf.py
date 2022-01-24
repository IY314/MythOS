from src.utils import ExecExit


def run(*args):
    if not len(args):
        raise ExecExit
    elif len(args) == 1:
        print(args[0])
    print(args[0] % args[1:])
