# -*- coding: utf-8 -*-
"""
Created on october 30 2015

@author: monteiro

Description:
    for files: renames the file accodingly
    for folders:
        1) iterates over folders renaming all files
        2) iterates over subfolders renaming all sub folders
"""
import logging
import argparse
import os

# parsing
parser = argparse.ArgumentParser()
parser.add_argument('--verbose', help='puts the program in verbose mode',
                    action="store_true", default=False)
parser.add_argument('--input', help='input path for file or folder to be'
                    'renamed', default=os.path.expandvars(
                        '$HOME/bin/git/batch_renamer/example'),
                    required=False)
parser.add_argument('--historyfile', help='destination of the history file',
                    default=os.path.expandvars('$HOME/bin/git/batch_renamer/'
                                               'history_file.txt'),
                    required=False)
# in case the argument is given without the input option
parser.add_argument('remainder', nargs=argparse.REMAINDER)

# checking parsed args and correcting
args = parser.parse_args()
if len(args.remainder) == 1:
    args.input = args.remainder[0]
    del args.remainder
elif len(args.remainder) > 1:
    raise Exception('More than one arguments were given'
                    'without parameters. Try using --input')
if os.path.isdir(args.input) is True or os.path.isfile(args.input) is True:
    pass
else:
    raise Exception('Path {0} does not exist'.format(args.input))

# logging
if args.verbose is True:
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                        level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')


for (root_dir, subdirs, file_names) in os.walk(args.input, topdown=False):
    print(root_dir)
    print(subdirs)
    print(file_names)
    input()
    names = dict()
    for file in file_names:
        primitive_n = primitive_name(file)
        if primitive_n not in names.keys():
            names[primitive_n] = []
        names[primitive_n].append(file)
    for key, value in names.items():
        elif len(value) == 1:
            new_name = primitive_name(value[0])
        elif len(value) > 1:
            new_name = create_new_name(key)



























