"""Execute a batch renaming of your files according to specific rules.

Mainly it takes off special characters and dashes leaving only letters,
numbers, underscores and periods.

The user can specify patterns (python regexes) to be ignored during the
renaming process.

Operation mode:
    1) Iterates over folders, starting at the deepest depths and moving
    backwards.
    2) Renames files accordingly.
    3) Renames subfolders.

"""

import logging
import argparse
import os
import shutil
import time
import collections
import re

from batch_renamer import (
    primitive_name, add_trailing_number,
    filter_out_paths_to_be_renamed,
    directory_generation_starting_from_files)


# # pylama:skip=1
# Ignore the % in formatting in logging (w1202)
# The '# noqa' ignores one line from pylama
# pylama:ignore=W1202,D103,D406,D407


# Mechanics related section.
def load_exclude_pattern_file(cli_args):
    with open(cli_args.excludepatternfile, 'rt') as excludepatternfile:
        excluded_patterns = excludepatternfile.read().splitlines()
        excluded_patterns = list(
            filter(
                lambda x: False if re.search('^\#', x) else True,
                excluded_patterns))
    logging.info('Exclude pattern file: {0}'.format(
        cli_args.excludepatternfile))
    logging.info('Excluding the following patterns:\n\t{0}'.format(
        '\n\t'.join(excluded_patterns)))
    if excluded_patterns:
        list_of_excl_regex_patterns = list(map(
            re.compile, excluded_patterns))
    else:
        list_of_excl_regex_patterns = list()

    return list_of_excl_regex_patterns


def deduplicate_names(names):
    # TODO: cover the case when the basenamed file already exists.
    # In this case an extra duplicated index should be appended then removed to
    # prevent overwritting of the file that already exists.

    # Solve the duplicate names problem by first creating a default dict whose
    # keys (primitive names) point to the number of indexes. By filtering ones
    # with more than one index one can find out the duplicate names.
    duplicate_names = collections.defaultdict(list)
    for index, item in enumerate(names):
        duplicate_names[item].append(index)
    duplicate_names = {k: v for k, v in duplicate_names.items() if len(v) > 1}

    if duplicate_names:
        # List is modified inplace: add the trailing number.
        # TODO: XXX urgent need to have more than one batch of duplicate_names
        # in a single run. The for below must be a two level nested for.
        for duplicate_indexes in duplicate_names.values():
            # TODO: error here, is not modified inplace anymore.
            names = add_trailing_number(names, n=len(duplicate_indexes))
    return names


def execute_renaming(old_names, new_names, args):
        # TODO: improve the security of this function. All of the new_names
        # shall be unique.
        # All of the new names shall not yet exist.

        list_of_file_renamings = []
        for src, dst in zip(old_names, new_names):
            if os.path.exists(dst):
                raise FileExistsError(
                    'WARNING: WILL NOT OVERWRITE FILE {0} -> {1}'.format(
                        src, dst))
            try:
                shutil.move(src, dst)
            except PermissionError:
                logging.warning(
                    'PermissionError exception: \'{}\''.format(src))
            except FileNotFoundError:
                logging.warning(
                    'FileNotFound exception: \'{}\''.format(src))
            else:
                # Store the file names with quotes escaped.
                list_of_file_renamings.append((
                    dst.replace("\"", "\\\""),
                    src.replace("\"", "\\\"")))
                logging.info("mv \"{1}\" \"{0}\"".format(dst, src))
        # Revert tuple to preserve renaming order (start with
        # subfolder).
        list_of_file_renamings = reversed(list_of_file_renamings)
        list_of_file_renamings = (
            'mv "{0}" "{1}"'.format(
                x[0],
                x[1]) for x in list_of_file_renamings)

        with open(args.historyfile, 'at') as history_file:
            history_file.write('\n'.join(list_of_file_renamings))
            history_file.write('\n')


# History file related section.
def get_last_id_from_change_in_historyfile(historyfile):
    HEADER_START = '## NEW ENTRY: '
    with open(historyfile, 'rt') as f:
        for i, line in enumerate(f, 1):
            if line.startswith(HEADER_START):
                change_number = i
    return change_number


def write_header_to_historyfile(historyfile):
    HEADER_START = '## NEW ENTRY: '
    with open(historyfile, 'rt') as history_file:
        change_number = len(history_file.read().splitlines())
    header = (
        HEADER_START
        + '|' + str(change_number) + '|'
        + 'at time ' + time.ctime()
        + '\n')
    with open(historyfile, 'at') as history_file:
        history_file.write(header)


def get_range_from_history_file(args):
    if args.revert == 'last':
        start_change_number = get_last_id_from_change_in_historyfile(
            args.historyfile)
        end_change_number = None
    else:
        start_change_number = args.revert
        with open(args.historyfile, 'rt') as f:
            for i, line in enumerate(
                    f.read().splitlines()[start_change_number:],
                    1):
                if line.startswith(HEADER_START):
                    end_change_number = (start_change_number
                                         + i
                                         + 1)  # include this line as well.
    return (start_change_number, end_change_number)



def get_rename_changes_from_historyfile(historyfile, change_range):
    mv_regex = re.compile(r'^mv "(.+?)(?<!\\)" "(.+?)(?<!\\)"$')
    with open(historyfile, 'rt') as f:
        regex_map = map(
            mv_regex.search,
            f.read().splitlines()[change_range[0]:change_range[1]])
        inverted_regex_map = map(
            lambda x: (x.group(1), x.group(2)),
            regex_map)
    return inverted_regex_map



# Test related section.
def create_batch_renamer_parser():
    # Arguments parsing block.
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--verbose',
        help=('Puts the program in verbose mode. Repeat this flag to go into'
              ' debug mode.'),
        action='count')

    parser.add_argument(
        '--input',
        nargs='+',  # Generates a list of input arguments.
        help='Input path for file or folder to be renamed.',
        default=False,
        required=False)

    parser.add_argument(
        '--revert',
        nargs='?',  # Consume one argument; if not present use default.
        help=('Revert the change of number N in the history file. If not '
              'specified revert the last change.'),
        const='last',
        default=False,
        required=False)

    parser.add_argument(
        '--historyfile',
        help='Destination of the history file. This file records any changes '
        'to allow the user to revert them if needed.',
        required=False)

    parser.add_argument(
        '--excludepatternfile',
        help='Do not rename files whose full path is a '
        'match in any of the re contained in this file.',
        required=False)

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

    return parser


# Cli related section.
def parse_arguments():
    """Parse arguments provided in the command line.

    Returns:
        argparse.ArgumentParser: the parsed arguments.

    """
    parser = create_batch_renamer_parser()

    # Checking parsed args and correcting.
    args = parser.parse_args()

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
    return args


def logging_setup(verbose):
    """Set up logging."""
    # Activates logging.
    if verbose is None:
        pass
    if verbose == 1:
        logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s',
                            level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')
        logging.info('Verbose mode.')
    if verbose == 2:
        # TODO: create a debug utility.
        pass
    return None


def check_arguments(args):
    """Check if arguments are valid.

    Do not initalize them.
    """
    # First check if either (exclusive) or 'input' or 'revert' is specified.
    if not (bool(args.input) ^ bool(args.revert)):
        raise ValueError(
            "The '--input' ({0}) and '--revert' ({1}) flags shall not be "
            "specified togeter".format(args.input, args.revert))

    # In both cases history file must be mentioned.
    if not os.path.isfile(args.historyfile):
        raise FileNotFoundError(
            'History file {0} does not exist'.format(args.historyfile))
    else:
        logging.info('History file: {0}'.format(args.historyfile))

    # For the case of args.input being truthy.
    if args.input:
        # Arguments checking
        # Check if input, historyfile and excludepatternfile exist.
        test_input_paths = list(map(os.path.exists, args.input))
        if not all(test_input_paths):
            raise FileNotFoundError(
                'Some of the input paths do not exist:\n\t{0}'.format(
                    '\n\t'.join(
                        list(filter(lambda x: not os.path.exists(x),
                                    args.input)))))
        else:
            # It is better to create a dictionary of 'files' and 'folders' in
            # order to process all the files first. Otherwise some file names
            # would be dependent on folders renames.
            logging.info('Processing paths: {0}'.format(
                '\n\t'.join(args.input)))

        if not os.path.isfile(args.excludepatternfile):
            raise FileNotFoundError(
                'Exclude pattern file {0} does not exist'.format(
                    args.excludepatternfile))
        else:  # Initializes the excluded patterns list of file exists.
            logging.info('History file: {0}'.format(args.excludepatternfile))

        # Parsing the prefix iso mod date mode.
        if args.prefixisomoddate:
            logging.info('Prefixing files according to \'yyymmdd_\'.')
        # Logging messages for the remaining arguments: prefix iso mod date and
        # dry run
        if args.dryrun:
            logging.info('Dry run mode: no actual changes will be made')
    # For the case of args.revert being truthy.
    elif args.revert:
        # TODO: parse the history file for the last number and adjust it.
        pass

    return None


# Main section.
def rename_files(args):
    # Constants declaration.
    RE_COMPILED_NOT_ALLOWED_EXPR = re.compile('[^a-z0-9\_\.]', flags=0)

    # Setup logging.
    logging_setup(args.verbose)

    # Load list of excluded regex patterns.
    list_of_excl_regex_patterns = load_exclude_pattern_file(args)

    write_header_to_historyfile(args.historyfile)

    # First filtering all the files that need to be renamed with
    # RE_COMPILED_NOT_ALLOWED_EXPR.
    # Then we filter the excluded patterns given in excludepatternfile in
    # list_of_excl_regex_patterns.
    # Both are accomplisshed in one step.
    input_args = dict()
    input_args['files'] = list(filter(os.path.isfile, args.input))
    input_args['folders'] = list(filter(os.path.isdir, args.input))
    for recurse in directory_generation_starting_from_files(
            input_args['files'],
            input_args['folders']):
        paths_to_rename = filter_out_paths_to_be_renamed(
            recurse,
            RE_COMPILED_NOT_ALLOWED_EXPR,
            list_of_excl_regex_patterns,
            args.prefixisomoddate)
        new_names = list(primitive_name(x) for x in paths_to_rename)

        # Deduplicate names.
        new_names = deduplicate_names(new_names)

        execute_renaming(paths_to_rename, new_names, args)

def revert_rename_files(args):
    change_range = get_range_from_history_file(args)

    map_of_tuples_to_be_renamed = get_rename_changes_from_historyfile(
        args.historyfile, change_range)

    old_names, new_names = zip(*map_of_tuples_to_be_renamed)

    execute_renaming(old_names, new_names, args)

def main(args):
    """Execute the actual renaming of files."""

    # Execute rename of files.
    if args.input:
        rename_files(args)
    # Execute restore of file names.
    elif args.revert:
        revert_rename_files(args)


if __name__ == '__main__':
    args = parse_arguments()
    main(args)
