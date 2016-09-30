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
import collections  # Used to find duplicate values and thus add
                    # a suffix accordingly.
import re
from batch_renamer import primitive_name, add_trailing_number, \
    filter_out_paths_to_be_renamed


def main():

    # Allowed regex to filter files that need to be renamed.
    # That is characters that are NOT:
    #   1) Lowercase letters
    #   2) Numbers
    #   3) Underscores
    #   4) Dots
    RE_COMPILED_NOT_ALLOWED_EXPR = re.compile('[^a-z0-9\_\.]', flags=0)

    # Variables parsing block.
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--verbose',
        help='Puts the program in verbose mode. Repeat this flag to go into'
        ' debug mode.',
        action='count')

    parser.add_argument(
        '--input',
        nargs='+',  # Generates a list of input arguments.
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


    parser.add_argument(
        '--dryrun',
        help='Print dummy commands to stdout without actually renaming '
        'the files.',
        action='store_true',
        default=False)

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
        if isinstance(getattr(args, atr), str):
            setattr(args,
                    atr,
                    os.path.abspath(
                    getattr(args, atr)))
        elif isinstance(getattr(args, atr), list):
            setattr(args,
                    atr,
                    list(map(
                        os.path.abspath,
                        getattr(args, atr))))

    # Check if input, historyfile and excludepatternfile exist.
    test_input_paths = list(map(os.path.exists, args.input))
    if not all(test_input_paths):
        raise FileNotFoundError(
            'Some of the input paths do not exist:\n\t{0}'.format(
            '\n\t'.join(
                list(filter(lambda x: not os.path.exists(x),
                            args.input)))))
    else:
        # It is better to create a dictionary of 'files' and 'folders' in order
        # to process all the files first. Otherwise some file names would be
        # dependent on folders renames.
        input_args = dict()
        input_args['files'] = list(filter(os.path.isfile, args.input))
        input_args['folders'] = list(filter(os.path.isdir, args.input))
        logging.info('Processing paths:\n\t{0}'.format(
            '\n\t'.join(args.input)))

    if not os.path.isfile(args.historyfile):
        raise FileNotFoundError(
            'History file {0} does not exist'.format(args.historyfile))
    else:
        logging.info('History file: {0}'.format(args.historyfile))

    if not os.path.isfile(args.excludepatternfile):
        raise FileNotFoundError(
            'Exclude pattern file {0} does not exist'.format(
                args.excludepatternfile))
    else:  # Initializes the excluded patterns list of file exists.
        with open(args.excludepatternfile, 'rt') as excludepatternfile:
            excluded_patterns = excludepatternfile.read().splitlines()
            excluded_patterns = list(
                filter(
                    lambda x: False if re.search('^\#', x) else True,
                    excluded_patterns))
        logging.info('Exclude pattern file: {0}'.format(
            args.excludepatternfile))
        logging.info('Excluding the following patterns:\n\t{0}'.format(
            '\n\t'.join(excluded_patterns)))


    # Parsing the prefix iso mod date mode.
    if args.prefixisomoddate:
        import datetime
        logging.info('Prefixing files according to \'yyymmdd_\'.')
    # Logging messages for the remaining arguments: prefix iso mod date and
    # dry run
    if args.dryrun:
        logging.info('Dry run mode: no actual changes will be made')

    # Write to history file.
    # Ignore patterns.
    # Take prefix iso mod date into account.
    # If not dry run:
        # Log.
        # Rename.
    # Else just print.

    # The most scallable approach would be:
    #   1) Create a list of all files.
    #   2) Filter the ones who need to be renamed.
    #   3) Resolve all conflicts.
    #   4) Do the renaming.
    #   5) (Take all the logging into account.)
    # The problem with this approach is that a very long list could be generated
    # in a folder with a lot of subfolders and files. Maybe a list with some
    # thousand entries is not a very elegant solution. A regular root folder has
    # circa 1e6 inodes for example.
    #
    # A different approach is to do this in mini batches, executing the job on
    # per folder batches.
    # This will be the approached used on this software.
    if excluded_patterns:
        list_of_excl_regex_patterns = list(map(
            re.compile, excluded_patterns))
    else:
        list_of_excl_regex_patterns = list()

    with open(args.historyfile, 'at') as history_file:
        history_file.write('NEW ENTRY: ' + time.ctime() + '\n')
        # First filtering all the files that need to be renamed with
        # RE_COMPILED_NOT_ALLOWED_EXPR.
        # Then we filter the excluded patterns given in excludepatternfile in
        # list_of_excl_regex_patterns.
        # Both are accomplisshed in one step.
        files_to_rename = filter_out_paths_to_be_renamed(
            input_args['files'],
            RE_COMPILED_NOT_ALLOWED_EXPR,
            list_of_excl_regex_patterns)
        new_names = list(map(primitive_name, files_to_rename))

        # Solve the duplicate names problem by first creating a default dict
        # whose keys (primitive names) point to the number of indexes.
        # By filtering ones with more than one index one can find out the
        # duplicate names.
        duplicate_names = collections.defaultdict(list)
        for index, item in enumerate(new_names):
            duplicate_names[item].append(index)
        duplicate_names = {k:v for k, v in duplicate_names.items() if len(v)>1}
        # List is modified inplace: add the trailing number.
        for duplicate_indexes in duplicate_names.values():
            add_trailing_number(new_names, duplicate_indexes)

        list_of_file_renamings = []
        for src, dst in zip(files_to_rename, new_names):
            try:
                os.rename(src, dst)
                list_of_file_renamings.append('mv \'{0}\' \'{1}\''.format(dst, src))
                logging.info('mv \'{1}\' \'{0}\''.format(dst, src))
            except PermissionError:
                pass

        # Then we can do the actual renaming of files.

        # Second we repeat the same procedure for the subdirectories.


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
