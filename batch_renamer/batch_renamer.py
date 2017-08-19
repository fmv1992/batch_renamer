"""Auxiliar functions for main program.

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
import datetime
import math

# pylama: ignore=E127,D407,D406

try:
    from unidecode import unidecode
except ImportError:
    def unidecode(x):
        """Declare dummy function in case unidecode package is not present."""
        return x


# TODO: prefix iso mod date is a different function. Move it to another one.
def primitive_name(x):
    """Create a primitive name from string x.

    Arguments:
        x (str): string to be converted to primitive name.

    Returns:
        str: string converted to primitive name.

    Examples:
        >>> primitive_name('i_dont_like_trailing_underscores__.tar')
        i_dont_like_trailing_underscores.tar
        >>> primitive_name('__pyname__')
        __pyname__

    """
    # Transliterate Unicode text into plain 7-bit ASCII if 'unicode' module is
    # present.
    basename = unidecode(os.path.basename(x)).lower()
    basename = re.sub(
        '''(?<=_)[^0-9a-zA-Z\_\.]+      # Match all non allowed chars
                                        # preceded by underline...
            |                           # ... or ...
            [^0-9a-zA-Z\_\.]+(?=_)''',  # All non allowed chars followed by
                                        # an underline.
        '',
        basename,
        flags=(re.VERBOSE))
    # Removes the leading chars if it is a symbol.
    basename = re.sub('^[^0-9a-zA-Z\_\.]+', '', basename)
    # Removes any sequence of non underscore chars for an underscore.
    basename = re.sub('[^0-9a-zA-Z\_\.]+', '_', basename)
    # Removes any trailings '_' before extension.
    basename = re.sub('_+(?=\.[^.]+$)', '', basename)
    # Removes any trailing '_'.
    basename = re.sub('_+$', '', basename)
    # TODO: improve the following obscure regex substitution.
    # Removes any sequence of '_' except at the start of the string.
    basename = re.search('^_*', basename).group()                             \
               + re.sub('_+', '_',
                        re.sub('(_*)([^_].+)', '\\2', basename))
    if basename == '':
        basename = '_'
    return os.path.join(os.path.dirname(x), basename)


def add_trailing_number(iterable_of_strs, suffix='_', n=None):
    """Add trailing number to strings in iterable_of_strs.

    Add a trailing number to string over and over again until there is not a
    file with that name.

    Arguments:
        iterable_of_strs (tuple): iterable_of_strs with strings to have
        trailing numbers added to it.
    TODO: add full description.

    Returns:
        map: strings with added trailing numbers.

    Example:
        >>> add_trailing_number(['a', 'b', 'c'])
        ('a_1', 'b_2', 'c_3')

    """
    if n is None:
        try:
            decimal_places = math.ceil(math.log(len(iterable_of_strs), 10))
        except TypeError:
            decimal_places = 0
    else:
        decimal_places = math.ceil(math.log(n, 10))
    return map(lambda i: i[1] + suffix + '{0:0{1}d}'.format(i[0],
                                                            decimal_places),
               enumerate(iterable_of_strs))


def prefix_iso_mod_date(file_path):
    """Prefix a filepath with a 'YYYY_MM_DD_' prefix according to mod date.

    Arguments:
        file_path (str): string to have a prefix added to.

    Returns:
        str: string with prepended prefix.

    Examples:
        >>> prefix_iso_mod_date('/tmp/dummy.txt')
        '/tmp/2017_01_01_dummy.txt'

    """
    basename = os.path.basename(file_path)
    iso_prefix = re.search('^[0-9]{8}_', basename)
    time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    if iso_prefix is None:
        basename = time.strftime('%Y%m%d_') + basename
    else:
        if iso_prefix.groups(0) != time.strftime('%Y%m%d_'):
            basename = time.strftime('%Y%m%d_') + basename[9:]
        else:
            basename = time.strftime('%Y%m%d_') + basename

    return os.path.join(os.path.dirname(file_path), basename)


def filter_out_paths_to_be_renamed(
        list_of_paths,
        compiled_regex_to_trigger_renaming,
        list_of_excluding_regex_patterns,
        prefixisomoddate):
    u"""Remove paths that need not to be renamed from a list.

    Arguments:
        list_of_paths (list): list of valid paths to be filtered.
        compiled_regex_to_trigger_renaming (compiled re object):
            compiled object whose search method should yield True for objects
            to be renamed.
        list_of_excluding_regex_patterns (list): list of patterns to remove a
            given path from the renaming process.

    Returns:
        list: A list contaning paths to be renamed.

    """
    paths_to_rename = filter(
        compiled_regex_to_trigger_renaming.search,
        list_of_paths)
    if prefixisomoddate:
        has_not_prefixisomoddate_regex = re.compile('^(?![0-9]{8}_)')
        paths_to_rename_prefixidomoddate = filter(
            has_not_prefixisomoddate_regex.search,
            list_of_paths)
        # This allows directories to come before files.
        paths_to_rename = set(paths_to_rename) \
                          | set(paths_to_rename_prefixidomoddate)  # noqa
        # This sorting makes sure files are processed first. Apply set to
        # variables disarranges the order.
        paths_to_rename = sorted(paths_to_rename, key=os.path.isfile,
                                 reverse=True)
    # Keep the entry if the exclude pattern search finds nothing.
    for exclude_pattern in list_of_excluding_regex_patterns:
        paths_to_rename = [
            x for x in paths_to_rename if exclude_pattern.search(x) is None
        ]
    return paths_to_rename


def do_the_renaming(old_names, new_names, history_file):
    u"""Remove paths that need not to be renamed from a list.

    Arguments:
        list_of_paths (list): list of valid paths to be filtered.
        compiled_regex_to_trigger_renaming (compiled re object):
            compiled object whose search method should yield True for objects a
            to be renamed.
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
        # In order to achieve consistency return a list of a single item.
        # Otherwise returning a string could mess with the functions that
        # iterate over an entry.
        yield [one_file]
    for one_dir in list_of_directories_to_recurse:
        for dirpath, _, filenames in os.walk(one_dir, topdown=False):
            yield [os.path.join(dirpath, fn) for fn in filenames] + [dirpath]


def generate_folder_structure(top):
    """Return a generator of all subfolders and files found in top directory.

    The order of returning the subfolders first or the files first does not
    matter as long as when the reverse operation is done if ones wants to
    restore the files.

    Arguments:
        top (str): the path of the directory to scan for all files.

    Returns:
        generator: a generator containing all files found recursively on top.

    """
    walk_w_folders = filter(
        lambda x: x[1],
        os.walk(top))
    for has_directory in walk_w_folders:
        for one_directory in has_directory[1]:
            yield os.path.join(has_directory[0], one_directory)

    walk_w_files = filter(
        lambda x: x[2],
        os.walk(top))
    for has_file in walk_w_files:
        for one_file in has_file[2]:
            yield os.path.join(has_file[0], one_file)
    return None


if __name__ == '__main__':
    pass
