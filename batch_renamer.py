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
        return re.sub('\W', '', x, re.ASCII)


def clean_name(x):
    """

    """
    x = unidecode(x).lower()
    # changes any symbol for '_'
    x = re.sub('(_+|[^\-\.A-Za-z0-9]+)', '_', x)
    x = re.sub('_(?=\.[^.]+$)', '', x)  # removes any trailing '_'
    x = re.sub('_+$', '', x)
    return x


def if_it_does_not_exist_then_rename(parent_path, old_name, new_name,
                                     ):
    i = 0
    while os.path.isfile(os.path.join(parent_path, new_name)) is True:
        new_name = re.sub('[0-9]+\.(?=[^.]+$)',
                          str('{0:02d}.'.format(i)),
                          new_name)
        i += 1
    while os.path.isdir(os.path.join(parent_path, new_name)) is True:
        new_name = re.sub('[0-9]+\.(?=[^.]+$)',
                          str('{0:02d}.'.format(i)),
                          new_name)
        i += 1
    # do the renaming
    print(old_name, '|->', new_name)
    os.rename(os.path.join(parent_path, old_name),
              os.path.join(parent_path, new_name))
    return True
