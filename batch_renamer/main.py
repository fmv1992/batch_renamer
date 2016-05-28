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
import pathlib
from batch_renamer import primitive_name, add_trailing_number
import re

#if __name__ == '__main__':
    #print(os.path.getmtime(__file__))
    #raise Exception

two_level_parent_folder = pathlib.Path(os.path.abspath(__file__)).parents[1]

# Parsing block
parser = argparse.ArgumentParser()
parser.add_argument('--verbose',
                    help='Puts the program in verbose mode.',
                    action="store_true",
                    default=False)
parser.add_argument('--input', help='Input path for file or folder to be '
                    'renamed.',
                    required=True)
parser.add_argument('--historyfile',
                    help='Destination of the history file. This file records'
                    'any changes to allow the user to revert them if needed.',
                    default=two_level_parent_folder/'history_file.txt',
                    required=True)
parser.add_argument('--excludepatternfile',
                    help='Exclude re patterns in the file.',
                    default=two_level_parent_folder/'exclude_re_patterns.txt',
                    required=False)
parser.add_argument('--prefixisomoddate',
                    help='Prefixes the filename with its last modified date '
                    'in ISO format: YYYYMMDD. It does not apply to folders.',
                    action="store_true",
                    default=False)

# Checking parsed args and correcting
args = parser.parse_args()
args.input = pathlib.Path(os.path.abspath(args.input))
args.excludepatternfile = pathlib.Path(os.path.abspath(args.excludepatternfile))

if args.prefixisomoddate:
    import datetime
# If args.historyfile is not default it need to be converted to pathlib.Path
args.historyfile = pathlib.Path(os.path.abspath(args.historyfile))
if args.input.is_file() is True or args.input.is_dir() is True:
    pass
else:
    raise Exception('Path {0} does not exist'.format(args.input))
if not args.historyfile.is_file():
    with args.historyfile.open('at') as history_file:
        history_file.write('')

# Logging
if args.verbose is True:
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                        level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')

if args.excludepatternfile.is_file():
    with args.excludepatternfile.open('rt') as excludepatternfile:
        excluded_patterns = excludepatternfile.read().splitlines()
        excluded_patterns = list(
                            filter(
                            lambda x: False if re.search('^\#', x) else True,
                            excluded_patterns))
else:
    excluded_patterns = []

with args.historyfile.open('at') as history_file:
        history_file.write('NEW ENTRY: ' + time.ctime() + '\n')
        for (root_dir, subdirs, file_names) in                                \
                       os.walk(os.path.join(*args.input.parts), topdown=False):
            for file_n in file_names:
                # Ignore patterns in 'exclude_re_patterns'
                for exclude_pattern in excluded_patterns:
                    if re.search(exclude_pattern,
                                 os.path.join(root_dir, file_n)):
                        break
                else:
                    primitive_n = primitive_name(os.path.join(root_dir,
                                                              file_n))
                    # If the new name is different than the actual name
                    # or the prefixisomoddate flag is True
                    if args.prefixisomoddate is True:
                        if re.search('\/[0-9]{8}_[^\/].*',
                                                          primitive_n) is None:
                            time = datetime.datetime.fromtimestamp(
                              os.path.getmtime(os.path.join(root_dir, file_n)))
                            primitive_n = os.path.join(
                                                  os.path.dirname(primitive_n),
                      time.strftime('%Y%m%d_') + os.path.basename(primitive_n))
                    if primitive_n != os.path.join(root_dir, file_n):
                        # If new name exists add a trailing number to new file
                        if os.path.exists(primitive_n):
                            dst = os.path.join(
                                    root_dir, add_trailing_number(primitive_n))
                        else:
                            dst = os.path.join(root_dir, primitive_n)
                        src = os.path.join(root_dir, file_n)
                        history_file.write('mv \'{0}\' \'{1}\'\n'.format(dst,
                                                                         src))
                        os.rename(src, dst)
            for dir_n in subdirs:
                for exclude_pattern in excluded_patterns:
                    if re.search(exclude_pattern, os.path.join(root_dir,
                                                               file_n)):
                        break
                else:
                    primitive_n = primitive_name(os.path.join(root_dir, dir_n))
                    # If the new name is different than the actual name
                    if primitive_n != os.path.join(root_dir, dir_n):
                        # If new name exists add a trailing number to new file
                        if os.path.isdir(primitive_n):
                            dst = os.path.join(
                                    root_dir, add_trailing_number(primitive_n))
                        else:
                            dst = os.path.join(root_dir, primitive_n)
                        src = os.path.join(root_dir, dir_n)
                        history_file.write('mv \'{0}\' \'{1}\'\n'.format(dst,
                                                                         src))
                        os.rename(src, dst)

# If it is a file and also the input itself
with args.historyfile.open('at') as history_file:
    history_file.write('NEW ENTRY: ' + time.ctime() + '\n')
    file_n = os.path.join(*args.input.parts)
    for exclude_pattern in excluded_patterns:
        if re.search(exclude_pattern, file_n):
            raise SystemExit(0)
    else:
        file_n = primitive_name(file_n)
        if os.path.exists(file_n):
            dst = add_trailing_number(primitive_n)
        src = os.path.join(*args.input.parts)
        dst = file_n
        history_file.write('mv \'{0}\' \'{1}\'\n'.format(dst, src))
        os.rename(src, dst)
