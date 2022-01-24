import os


def _find_all(filename, paths):
    for path in paths:
        if os.path.isfile(os.path.join('.', 'root', *path, filename)):
            yield ['root', *path, filename]


def find(filename, paths):
    result = tuple(_find_all(filename, paths))
    if result:
        return result[0]
    return None


def find_all(filename, paths):
    return tuple(_find_all(filename, paths))
