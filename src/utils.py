"""Utility functions."""

import json


class ExecExit(Exception):
    """Exception thrown to exit a program."""

    pass


def callterm(*calls, newline=False, flush=True):
    """
    Call a terminal code.

    Args:
        *calls: the terminal codes to call
        newline: whether to print a newline after the calls
        flush: whether to flush the output after the calls

    Returns:
        None
    """
    print(*calls, sep='', end='', flush=flush)
    if newline:
        print()


def clearterm(term, extent='screen', location=(0, 0)):
    """
    Clear the terminal.

    Args:
        term: the terminal instance to use
        extent: the extent to clear (default: 'screen')
        location: the location to start clearing from (default: (0, 0))

    Returns:
        None
    """
    if extent == 'screen':
        attr = term.clear
    elif extent == 'line':
        attr = term.clear_bol + term.clear_eol
    else:
        raise ValueError(f"Invalid argument for 'extent': {extent!r}")
    callterm(term.move_yx(*location), attr, term.normal)
    if extent == 'screen':
        # Display top bar
        with open('mythos/mythos.json') as f:
            version_number = json.load(f)['version']
        callterm(
            term.center(f' MythOS v{version_number} ', fillchar='='),
            newline=True
        )
        print()
    # Adjust column
    callterm(term.move_x(0))


def get_input(
        term,
        prompt,
        *,
        default=None,
        hide=False,
        condition=lambda _: None,
        hook=None
        ):
    """
    Get input from the user.

    Args:
        term: the terminal
        prompt: the prompt to display
        default: the default value to use if the user does not enter anything
        hide: whether to hide the input from the user
        condition: a function that returns a message if the input is invalid
        hook: a function that is called after the input is valid

    Returns:
        The input, or -1 if the user wants to cancel
    """
    user_input = ''
    display = ''
    print(prompt, end='')
    while (key := term.inkey()).code != term.KEY_ENTER:
        if not key.is_sequence:
            user_input += key
            display += '*' if hide else key
        elif key.code == term.KEY_BACKSPACE:
            user_input = user_input[:-1]
            display = display[:-1]
        elif key.code == term.KEY_ESCAPE:
            return -1
        clearterm(term, 'line', term.get_location())
        print(f'{prompt}{display}', end='')

    if msg := condition(user_input):
        print(f'\n{msg}')
        return get_input(term, prompt, default, hide, condition)

    print()
    if hook:
        return hook(user_input)
    return user_input
