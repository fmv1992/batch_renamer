# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 21:41:03 2015

@author: monteiro

Description: renames files according to some rules:
RULES:
1) There are exceptions. File names that match those exceptions are ignored.
2) Transliterate Unicode text into plain 7-bit ASCII if the 'unicode' module is
present.
3) Changes uppercase to lower case.
4) Remove spaces and other symbols and puts underlines in their place.

"""
import re
import os

try:
    from unidecode import unidecode
except ImportError:
    def unidecode(x):
        return x


def primitive_name(x, add_trailing_numbers=False):
    """
    Creates a primitive name from string x.
    """
    # Transliterate Unicode text into plain 7-bit ASCII if 'unicode' module is
    # present
    basename = unidecode(os.path.basename(x)).lower()
    # Changes a sequence of symbols for a single underline if it is not
    # adjacent to an underline. In this case obliterates the symbol.
    # Symbols are any character which is not a letter, nor a number nor '.' and
    # '_'
    for found_patterns in re.findall('''(?<=_)[^0-9a-zA-Z\_\.]+  #
                                     |                           #
                                     [^0-9a-zA-Z\_\.]+(?=_)''', basename, re.VERBOSE):
        basename = basename.replace(found_patterns, '')
    basename = re.sub('[^0-9a-zA-Z\_\.]+', '_', basename)
    # Removes any trailing '_' before extension
    basename = re.sub('_(?=\.[^.]+$)', '', basename)
    # Removes any trailing '_'
    basename = re.sub('_+$', '', basename)
    # Removes any sequence of '_' except at the start of the string
    basename = re.match('_*', basename).group() + re.sub('_+', '_', re.sub('(_*)([^_].+)', '\\2', basename))
    if basename == '':
        basename = 'empty_name_after_e
    return os.path.join(os.path.dirname(x), basename)


def add_trailing_number(x):
    """
    Adds a trailing number to string over and over again until there is not a
    file with that name.
    """
    basename = os.path.basename(x)
    # Takes into account that a file could already be names with '_00.txt' for
    # example. This instead of creating "_00_00" it considers that sufix.

    # for the case that has an extension
    if '.' in basename:
        basename = re.sub('_[0-9]{2,3}(?=.[a-zA-Z0-9]+[\.a-zA-Z0-9]+$)', '', basename)
        i = 0
        while os.path.isfile(os.path.join(
                             os.path.dirname(x), basename)) is True:
            basename = re.sub('_[0-9]{2,3}(?=.[a-zA-Z0-9]+[\.a-zA-Z0-9]+$)', '', basename)
            basename = re.search('^[^\.]*', basename).group() + '_{0:02d}'.format(i) + re.search('\.[a-zA-Z0-9]+[\.a-zA-Z0-9]+$', basename).group()
            i += 1
#    elif os.path.isdir(os.path.join(os.path.dirname(x), basename)):
#            i = 0
#            while os.path.isdir(os.path.join(
#                                os.path.dirname(x), basename)) is True:
#                if re.match('[0-9][0-9]$', basename):
#                    basename = re.sub('[0-9][0-9]$',
#                                      str('{0:02d}'.format(i)),
#                                      basename, count=1)
#                else:
#                    basename += str('_{0:02d}'.format(i))
#                i += 1
    return os.path.join(os.path.dirname(x), basename)
