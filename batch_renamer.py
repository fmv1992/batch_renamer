# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 21:41:03 2015

@author: monteiro

Description: renames all files; simple as that
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

    """
    basename = unidecode(os.path.basename(x)).lower()
    # changes not allowed chars for '_'
    basename = re.sub('[^0-9a-zA-Z\_\.]', '_', basename)
    # removes any trailing '_' before extension
    basename = re.sub('_(?=\.[^.]+$)', '', basename)
    # removes any trailing '_'
    basename = re.sub('_+$', '', basename)
    # removes any sequence of '_' except at the start of the string
    basename = re.sub('(?<=[^^])_+', '_', basename)
    return os.path.join(os.path.dirname(x), basename)


def add_trailing_number(x):
    """

    """
    basename = os.path.basename(x)
    if os.path.isfile(os.path.join(os.path.dirname(x), basename)):
            i = 0
            while os.path.isfile(os.path.join(
                                 os.path.dirname(x), basename)) is True:
                if '.' in basename:
                    basename = re.sub('\.',
                                      str('_{0:02d}.'.format(i)),
                                      basename, count=1)
                elif re.match('[0-9][0-9]$', basename):
                    basename = re.sub('[0-9][0-9]$',
                                      str('{0:02d}'.format(i)),
                                      basename, count=1)
                else:
                    basename += str('_{0:02d}'.format(i))
                i += 1
    elif os.path.isdir(os.path.join(os.path.dirname(x), basename)):
            i = 0
            while os.path.isdir(os.path.join(
                                os.path.dirname(x), basename)) is True:
                if re.match('[0-9][0-9]$', basename):
                    basename = re.sub('[0-9][0-9]$',
                                      str('{0:02d}'.format(i)),
                                      basename, count=1)
                else:
                    basename += str('_{0:02d}'.format(i))
                i += 1
    return os.path.join(os.path.dirname(x), basename)
