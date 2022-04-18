import os


def _find_all(filename, paths):
    for path in paths:
        if os.path.isfile(os.path.join('.', 'mythos', 'root', *path, filename + '.py')):
            yield [True, 'root', *path, filename]


def find(filename, paths):
    if result := find_all(filename, paths):
        return result[0]
    return None


def find_all(filename, paths):
    return tuple(_find_all(filename, paths))
