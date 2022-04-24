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
