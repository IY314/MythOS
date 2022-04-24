"""Path utility functions."""

import os


def _find_all(filename, paths):
    for path in paths:
        if os.path.isfile(os.path.join(
            '.', 'mythos', 'root', *path, f'{filename}.py'
        )):
            yield [True, 'root', *path, filename]


def find(filename, paths):
    """
    Find the first file in paths that matches the filename.

    Args:
        filename: the filename to find
        paths: the paths to search

    Returns:
        The path to the file if found, otherwise None
    """
    if result := find_all(filename, paths):
        return result[0]
    return None


def find_all(filename, paths):
    """
    Find all files in paths that match the filename.

    Args:
        filename: the filename to find
        paths: the paths to search

    Returns:
        A tuple of paths to the files that match the filename
    """
    return tuple(_find_all(filename, paths))
