import os
from src.utils import callterm


def main(term, instance, *args):
    if len(args) > 1:
        instance.log(1, f'Arguments after {args[0]!r} are ignored')
    if args:
        dirname = args[0] if len(args) else instance.dirpath
        if os.path.isdir(dirname):
            for d in os.listdir(dirname):
                if os.path.isdir(os.path.join(dirname, d)):
                    callterm(term.turquoise1, d, term.normal, newline=True)
                else:
                    print(d)
