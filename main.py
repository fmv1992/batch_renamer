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
# imports
import logging
import argparse
import os
from batch_renamer import trimm_filename, trimm_foldername
from utilities.string_utilities import split_folder_and_filename, get_last_dir,\
split_filename_and_extension

# parsing
parser = argparse.ArgumentParser()
parser.add_argument('--verbose', help='puts the program in verbose mode',
                    action="store_true", default=False)
parser.add_argument('--input', help='input path for file or folder to be'     \
'renamed', default=os.path.expandvars('$HOME/downloads'), required=False)
    # in case the argument is given without the input option
parser.add_argument('remainder', nargs=argparse.REMAINDER)

args = parser.parse_args()
# checking and correcting args
if len(args.remainder) == 1:
    args.input = args.remainder[0]
    del args.remainder
elif len(args.remainder) > 1:
    raise Exception('More than one arguments were given'
                    'without parameters. Try using --input')
if os.path.isdir(args.input) is True or \
   os.path.isfile(args.input) is True:
       pass
else:
     raise Exception('Input path does not exist')
     
# logging
if args.verbose is True:
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                        level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')

#
duplicate_filenames = {}
duplicate_foldernames = {}    

# if is file
if os.path.isfile(args.input):
    (folder_path, file_name) = split_folder_and_filename(args.input)
    new_filename = trimm_filename(file_name)
    os.rename(args.input, str(folder_path + '/' + new_filename))

# if is folder    
else:
    for (root_dir, subdirs, file_names) in os.walk(args.input, topdown=False):
#        print(root_dir)
#        print(subdirs)
#        print(file_names)
        # fix filenames
        for one_filename in file_names:
            # if new name is different
            new_filename = trimm_filename(one_filename)
            src_path = str(root_dir + '/' + one_filename)
            dst_path = str(root_dir + '/' + new_filename)
            if dst_path in duplicate_filenames: # file already exists
                duplicate_filenames[dst_path].append(src_path)
            else:
                duplicate_filenames[dst_path] = [src_path]
        for (key, item) in duplicate_filenames.items():
            if len(item) > 1:
                for (i, one_dup_file) in enumerate(item):
                    destination_path = split_folder_and_filename(one_dup_file)[0] + '/' + \
                        split_filename_and_extension(key)[0] + '_' + \
                        str('{0:02d}'.format(i)) + \
                        split_filename_and_extension(one_dup_file)[1]
                    #print(repr(item[0]), '->', repr(key))
                    while os.path.isfile(destination_path):
                        i += 1
                        destination_path = split_folder_and_filename(one_dup_file)[0] + '/' + \
                        split_filename_and_extension(key)[0] + '_' + \
                        str('{0:02d}'.format(i)) + \
                        split_filename_and_extension(one_dup_file)[1]
                    try:
                        os.rename(one_dup_file, destination_path)
                    except PermissionError:
                        print('Permission error for', one_dup_file)
            else:
                #print(repr(item[0]), '->', repr(key))
                try:
                    os.rename(item[0], key)
                except PermissionError:
                    print('Permission error for', item[0])
        duplicate_filenames = {}
        # fix subdirs
        for subdir in subdirs:
            # if new name is different
            new_subdirname = trimm_filename(subdir)
            src_path = str(root_dir + '/' + subdir)
            dst_path = str(root_dir + '/' + new_subdirname)
            if dst_path in duplicate_foldernames: # file already exists
                duplicate_foldernames[dst_path].append(src_path)
            else:
                duplicate_foldernames[dst_path] = [src_path]
        for (key, item) in duplicate_foldernames.items():
            if len(item) > 1:
                for (i, one_dup_file) in enumerate(item):
                    if os.path.isdir(key):
                        destination_path = get_last_dir(one_dup_file)[0] + '/' + \
                            trimm_foldername(get_last_dir(one_dup_file)[1]) + '_' + \
                            str('{0:02d}'.format(i))
                        while os.path.isdir(destination_path) is True:
                            i += 1
                            #print(i)
                            destination_path = get_last_dir(one_dup_file)[0] + '/' + \
                                trimm_foldername(str(
                                get_last_dir(one_dup_file)[1] + '_' + \
                                str('{0:02d}'.format(i))
                                ))
                        key = destination_path
                    #print(repr(one_dup_file), '|->', repr(destination_path))
                    os.rename(one_dup_file, key)
            else:
                #print(repr(item[0]), '->', repr(key))
                try:
                    os.rename(item[0], key)
                except PermissionError:
                    print('Permission error for', item[0])
        duplicate_foldernames = {}