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


def clearterm(term):
    callterm(term.home, term.clear, term.normal)
    callterm(term.center(' MythOS v1.0.0 ', fillchar=f'='), newline=True)
    print()
