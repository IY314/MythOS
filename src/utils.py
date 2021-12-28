import json


def mod_input(prompt='>', *, type_=str, retry=False):
    while True:
        try:
            return type_(input(prompt))
        except ValueError:
            if not retry:
                return None


def callterm(*calls, newline=False, flush=False):
    print(*calls, sep='', end='', flush=flush)
    if newline:
        print()


def clearterm(term, extent='screen', location=(0, 0)):
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
            term.center(f' MythOS v{version_number} ', fillchar=f'='),
            newline=True
        )
        print()
    # Adjust column
    callterm(term.move_x(0), flush=True)
