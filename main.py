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
import time
from batch_renamer import primitive_name, add_trailing_number

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
args.input = os.path.abspath(args.input)
args.historyfile = os.path.abspath(args.historyfile)
if not os.path.exists(args.historyfile):
    with open(args.historyfile, 'wt') as f:
        f.write(0)
# logging
if args.verbose is True:
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                        level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')

with open(args.historyfile, 'at') as history_file:
        history_file.write('NEW ENTRY: ' + time.ctime() + '\n')
        for (root_dir, subdirs, file_names) in os.walk(args.input,
                                                       topdown=False):
            for file_n in file_names:
                primitive_n = primitive_name(os.path.join(root_dir, file_n))
                # if the new name is different than the actual name
                if primitive_n != os.path.join(root_dir, file_n):
                    # if new name exists add a trailing number to new file
                    if os.path.exists(primitive_n):
                        dst = os.path.join(root_dir,
                                           add_trailing_number(primitive_n))
                    else:
                        dst = os.path.join(root_dir, primitive_n)
                    src = os.path.join(root_dir, file_n)
                    history_file.write('mv \'{0}\' \'{1}\'\n'.format(dst, src))
                    os.rename(src, dst)
            for dir_n in subdirs:
                primitive_n = primitive_name(os.path.join(root_dir, dir_n))
                # if the new name is different than the actual name
                if primitive_n != os.path.join(root_dir, dir_n):
                    # if new name exists add a trailing number to new file
                    if os.path.exists(primitive_n):
                        dst = os.path.join(root_dir,
                                           add_trailing_number(primitive_n))
                    else:
                        dst = os.path.join(root_dir, primitive_n)
                    src = os.path.join(root_dir, dir_n)
                    history_file.write('mv \'{0}\' \'{1}\'\n'.format(dst, src))
                    os.rename(src, dst)