from utils import clearterm, callterm


def parse_args(text):
    pre_args = text.split()
    if not pre_args:
        return
    filename = pre_args[0]
    if len(pre_args) == 1:
        return filename, []
    args = pre_args[1:]
    return filename, args


def terminal(term, instance):
    clearterm(term)
    while True:
        prompt = f"{'/'.join(instance.dirpath)} % "
        callterm(prompt, flush=True)
        result = ''
        while (key := term.inkey()).code != term.KEY_ENTER:
            if not key.is_sequence:
                result += key
            elif key.code == term.KEY_BACKSPACE and result:
                result = result[:-1]
            clearterm(term, 'line', term.get_location())
            callterm(prompt, result, flush=True)
        if (parsed_args := parse_args(result)) is None:
            print()
            continue

        filename, args = parsed_args
        print()

        if exe := getattr(instance, f'builtin_{filename}', False):
            exe(*args)

        print()
