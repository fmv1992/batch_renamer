u"""
This module does a batch rename of your files according to specific rules.

Mainly it takes off special characters and dashes leaving only letters, numbers,
underscores and periods.

Operation mode:
    1) Iterates over folders, starting at the deepest depths and moving
    backwards.
    2) Renames files accordingly.
    3) Renames subfolders.

"""

# pylama:skip=1

import logging
import argparse
import os
import time
from batch_renamer import primitive_name, add_trailing_number
import re

def main():
    TWO_LEVEL_PARENT_FOLDER = os.path.abspath(
        os.path.dirname(
            os.path.dirname(
                __file__)))

    # Parsing block.
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--verbose',
        help='Puts the program in verbose mode. Repeat this flag to go into'
        ' debug mode.',
        action='count')

    parser.add_argument(
        '--input',
        help='Input path for file or folder to be renamed.',
        required=True)

    parser.add_argument(
        '--historyfile',
        help='Destination of the history file. This file records any changes '
        'to allow the user to revert them if needed.',
        required=True)

    parser.add_argument(
        '--excludepatternfile',
        help='Do not rename files whose full path is a '
        'match in any of the re contained in this file.',
        required=True)

    parser.add_argument(
        '--prefixisomoddate',
        help='Prefixes the filename with its last modified date '
        'in ISO format: YYYYMMDD_. It does not apply to folders.',
        action='store_true',
        default=False)

    # TODO: add argument for dry run

    # Checking parsed args and correcting.
    args = parser.parse_args()
    # Activates logging.
    if args.verbose is None:
        pass
    if args.verbose == 1:
        logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s',
                            level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')
        logging.info('Verbose mode.')
    if args.verbose == 2:
        # TODO: create a debug utility.
        pass

    # Expanding args attributes to full path.
    for atr in ['input', 'historyfile', 'excludepatternfile']:
        setattr(args,
                atr,
                os.path.abspath(
                   getattr(args, atr)))

    # Check if historyfile, excludepatternfile and input exist.
    if not os.path.isfile(args.historyfile):
        raise FileNotFoundError
    if not os.path.isfile(args.excludepatternfile):
        raise FileNotFoundError
    else:  # Initializes the excluded patterns list of file exists.
        with open(args.excludepatternfile, 'rt') as excludepatternfile:
            excluded_patterns = excludepatternfile.read().splitlines()
            excluded_patterns = list(
                filter(
                    lambda x: False if re.search('^\#', x) else True,
                    excluded_patterns))
        logging.info('Excluding the following patterns:\n\t{0}'.format(
            '\n\t'.join(excluded_patterns)))
    if not os.path.exists(args.input):
        raise FileNotFoundError

    if args.prefixisomoddate:
        import datetime

    raise Exception
    # Write to log file.
    # Ignore patterns.
    # Take prefix iso mod date into account.
    # If not dry run:
        # Log.
        # Rename.
    # Else just print.


# Old code
#    with args.historyfile.open('at') as history_file:
#            history_file.write('NEW ENTRY: ' + time.ctime() + '\n')
#            for (root_dir, subdirs, file_names) in                                \
#                    os.walk(os.path.join(*args.input.parts), topdown=False):
#                for file_n in file_names:
#                    # Ignore patterns in 'exclude_re_patterns'
#                    for exclude_pattern in excluded_patterns:
#                        if re.search(exclude_pattern,
#                                    os.path.join(root_dir, file_n)):
#                            break
#                    else:
#                        primitive_n = primitive_name(os.path.join(root_dir,
#                                                                file_n))
#                        # If the new name is different than the actual name
#                        # or the prefixisomoddate flag is True
#                        if args.prefixisomoddate is True:
#                            if re.search('\/[0-9]{8}_[^\/].*',
#                                        primitive_n) is None:
#                                time = datetime.datetime.fromtimestamp(
#                                    os.path.getmtime(os.path.join(
#                                        root_dir, file_n)))
#                                primitive_n = os.path.join(
#                                    os.path.dirname(primitive_n),
#                                    time.strftime('%Y%m%d_')
#                                    + os.path.basename(primitive_n))
#                        if primitive_n != os.path.join(root_dir, file_n):
#                            # If new name exists add a trailing number to new file
#                            if os.path.exists(primitive_n):
#                                dst = os.path.join(
#                                    root_dir, add_trailing_number(primitive_n))
#                            else:
#                                dst = os.path.join(root_dir, primitive_n)
#                            src = os.path.join(root_dir, file_n)
#                            try:
#                                os.rename(src, dst)
#                                history_file.write('mv \'{0}\' \'{1}\'\n'.format(dst,
#                                                                            src))
#                            except PermissionError:
#                                pass
#                for dir_n in subdirs:
#                    for exclude_pattern in excluded_patterns:
#                        if re.search(exclude_pattern, os.path.join(root_dir,
#                                                                file_n)):
#                            break
#                    else:
#                        primitive_n = primitive_name(os.path.join(root_dir, dir_n))
#                        # If the new name is different than the actual name
#                        if primitive_n != os.path.join(root_dir, dir_n):
#                            # If new name exists add a trailing number to new file
#                            if os.path.isdir(primitive_n):
#                                dst = os.path.join(
#                                    root_dir, add_trailing_number(primitive_n))
#                            else:
#                                dst = os.path.join(root_dir, primitive_n)
#                            src = os.path.join(root_dir, dir_n)
#                            try:
#                                os.rename(src, dst)
#                                history_file.write('mv \'{0}\' \'{1}\'\n'.format(dst,
#                                                                            src))
#                            except PermissionError:
#                                pass
#
#    # If it is a file and also the input itself
#    with args.historyfile.open('at') as history_file:
#        history_file.write('NEW ENTRY: ' + time.ctime() + '\n')
#        file_n = os.path.join(*args.input.parts)
#        for exclude_pattern in excluded_patterns:
#            if re.search(exclude_pattern, file_n):
#                raise SystemExit(0)
#        else:
#            file_n = primitive_name(file_n)
#            if os.path.exists(file_n):
#                dst = add_trailing_number(primitive_n)
#            src = os.path.join(*args.input.parts)
#            dst = file_n
#            if src != dst:
#                history_file.write('mv \'{0}\' \'{1}\'\n'.format(dst, src))
#                os.rename(src, dst)


if __name__ == '__main__':
    main()
