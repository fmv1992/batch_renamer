"""
Auxiliar functions for main program.

Multi
Line
Description
TODO

Functions:
    TODO
    f1
    f2

"""

import re
import os

try:
    from unidecode import unidecode
except ImportError:
    def unidecode(x):
        u"""Dummy function in case unidecode package is not present."""
        return x


def primitive_name(x, add_trailing_numbers=False):
    """
    Create a primitive name from string x.

    Arguments:
        x (str): string to be converted to primitive name.
        add_trailing_numbers (bool): whether or not to add a '_dd' suffix.

    Returns:
        str: string converted to primitive name.
    """
    # Transliterate Unicode text into plain 7-bit ASCII if 'unicode' module is
    # present
    basename = unidecode(os.path.basename(x)).lower()
    # Changes a sequence of symbols for a single underline if it is not
    # adjacent to an underline. In this case obliterates the symbol.
    # Symbols are any character which is not a letter, nor a number nor '.' and
    # '_'
    basename = re.sub(
        '''(?<=_)[^0-9a-zA-Z\_\.]+      # Match all non allowed chars
                                        # preceded by underline...
            |                           # ... or ...
            [^0-9a-zA-Z\_\.]+(?=_)''',  # All non allowed chars followed by
                                        # an underline.
        '',
        basename,
        flags=(re.VERBOSE))
    # Removes the first char if it is a symbol
    basename = re.sub('^[^0-9a-zA-Z\_\.]+', '', basename)
    # Removes any sequence of non underscore chars for an underscore
    basename = re.sub('[^0-9a-zA-Z\_\.]+', '_', basename)
    # Removes any trailing '_' before extension
    basename = re.sub('_(?=\.[^.]+$)', '', basename)
    # Removes any trailing '_'
    basename = re.sub('_+$', '', basename)
    # Removes any sequence of '_' except at the start of the string
    basename = re.search('^_*', basename).group()                             \
        + re.sub('_+', '_', re.sub('(_*)([^_].+)', '\\2', basename))
    if basename == '':
        basename = '_'
    return os.path.join(os.path.dirname(x), basename)


def add_trailing_number(list_of_paths, list_of_indexes_with_dupes):
    """
    Substitute or add a trailing number to the string.

    Add a trailing number to string over and over again until there is not a
    file with that name.

    Arguments:
        list_of_paths (list): list of paths with duplicate_names.
        list_of_indexes_with_dupes (list): list of integer indexes referring to
            list_of_paths with dupes.

    Returns:
        True: The input list is modified in place.

    """
    base_string = list_of_paths[list_of_indexes_with_dupes[0]]
    if '.' in base_string:
        file_name, extension = base_string.split('.', maxsplit=1)
        extension = '.' + extension
    else:
        file_name = base_string
        extension = ''
    decimal_places = 1
    number_of_elements = len(list_of_indexes_with_dupes)
    while number_of_elements/10 > 1:
        number_of_elements /= 10
        decimal_places += 1
    for i, index in enumerate(list_of_indexes_with_dupes):
        list_of_paths[index] = file_name \
            + '_{1:{0}d}'.format(decimal_places, i) \
            + extension
    return True


def filter_out_paths_to_be_renamed(
        list_of_paths,
        compiled_regex_to_trigger_renaming,
        list_of_excluding_regex_patterns):
    u"""Remove paths that need not to be renamed from a list.

    Arguments:
        list_of_paths (list): list of valid paths to be filtered.
        compiled_regex_to_trigger_renaming (compiled re object):
            compiled object whose search method should yield True for objects to
            be renamed.
        list_of_excluding_regex_patterns (list): list of patterns to remove a
            given path from the renaming process.

    Returns:
        list: A list contaning paths to be renamed.

    """
    # If the compiled regex to trigger renaming returns something keep this
    # entry.
    # Only considers basename in order to do the renaming.
    paths_to_rename = [x for x in list_of_paths if
                       compiled_regex_to_trigger_renaming.search(
                           os.path.basename(x)) is not None]
    # Keep the entry if the exclude pattern search finds nothing.
    for exclude_pattern in list_of_excluding_regex_patterns:
        paths_to_rename = [x for x in paths_to_rename if
                           exclude_pattern.search(x) is None]
    return paths_to_rename


def do_the_renaming(old_names, new_names, history_file):
    u"""Remove paths that need not to be renamed from a list.

    Arguments:
        list_of_paths (list): list of valid paths to be filtered.
        compiled_regex_to_trigger_renaming (compiled re object):
            compiled object whose search method should yield True for objects to
            be renamed.
        list_of_excluding_regex_patterns (list): list of patterns to remove a
            given path from the renaming process.

    Returns:
        list: A list contaning paths to be renamed.

    """
    pass


def directory_generation_starting_from_files(
        list_of_files,
        list_of_directories_to_recurse):
    u"""Return a single generator starting from files then folders."""
    for one_file in list_of_files:
        yield one_file
    for one_dir in list_of_directories_to_recurse:
        for dirpath, _, filenames in os.walk(
                one_dir, topdown=False):
            yield [os.path.join(dirpath, fn) for fn in filenames] + [dirpath]
