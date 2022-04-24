"""Shell functions."""

import path
from utils import clearterm, callterm


def parse_args(text):
    """
    Parse arguments from a string.

    Args:
        text: the string to parse

    Returns:
        A tuple of the filename and the arguments, or None if the string is
        invalid
    """
    pre_args = text.split()
    if not pre_args:
        return None
    filename = pre_args[0]
    if len(pre_args) == 1:
        return filename, []
    args = pre_args[1:]
    return filename, args


def terminal(term, instance):
    """
    Run a MythOS shell.

    Args:
        term: the terminal instance to use
        instance: the MythOS instance to use

    Returns:
        None
    """
    clearterm(term)
    while True:
        prompt = f"{'/'.join(instance.dirpath)} % "
        callterm(prompt)
        result = ''
        while (key := term.inkey()).code != term.KEY_ENTER:
            if not key.is_sequence:
                result += key
            elif key.code == term.KEY_BACKSPACE and result:
                result = result[:-1]
            clearterm(term, 'line', term.get_location())
            callterm(prompt)
        if (parsed_args := parse_args(result)) is None:
            print()
            continue

        filename, args = parsed_args
        print()

        if exe := getattr(instance, f'builtin_{filename}', False):
            exe(*args)
        elif (file := path.find(filename, instance.paths)) is not None:
            instance.run_file(file, *args)
        else:
            instance.log(3, f'Unknown command: {filename}')

        print()
