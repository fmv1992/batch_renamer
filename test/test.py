"""Test the batch_renamer module.

Tests should be:
    1) modular
    2) repeatable (like setting N=100)
"""

import string
import random
import os
import unittest
import tempfile
import datetime
import math
import hashlib
import sys

from batch_renamer.batch_renamer import primitive_name, generate_folder_structure, add_trailing_number, prefix_iso_mod_date  # noqa
import batch_renamer.main as brm


# pylama:ignore=D100,D101,D102,D103,E731
ALLOWED_SYMBOLS = set(('_', '.'))
ALLOWED_CHARS = set(string.ascii_lowercase)
ALLOWED = ALLOWED_SYMBOLS | ALLOWED_CHARS

PATH_RESERVED_SYMBOLS = set(('\\', '/'))
NON_ALLOWED_SYMBOLS = (set(string.punctuation)
                       - (ALLOWED_SYMBOLS | PATH_RESERVED_SYMBOLS))
NON_ALLOWED_CHARS = set(string.ascii_uppercase)

# Number of tests to run.
N = 10  # Number of strings in each folder.


def create_random_string(charset,
                         min_len=5,
                         max_len=10):
    charset_tuple = tuple(charset)
    return ''.join(random.choice(charset_tuple) for x in
                   range(random.randint(min_len, max_len)))


def create_file_extension():
    all_extensions = ('.txt', '.mp3', '.py', '.tar.xz', '.tar', )
    return random.choice(all_extensions)


def create_filename(
        charset,
        root_dir):
    if random.random() < 0.5:
        extension = create_file_extension()
    else:
        extension = ''
    return os.path.join(root_dir, create_random_string(charset) + extension)


def create_dirname(charset, root_dir):
    return os.path.join(root_dir, create_random_string(charset))


def populate_directory_with_files(
        charset,
        root_dir,
        n_min_files=5,
        n_max_files=10):

    n_files = random.randint(n_min_files, n_max_files)

    i = 0
    while i < n_files:
        fname = create_filename(charset, root_dir)
        if not os.path.isfile(fname):
            os.mknod(fname)
            i += 1


def populate_directory_with_dirs(
        charset,
        root_dir,
        n_min_dirs=5,
        n_max_dirs=10):

    n_files = random.randint(n_min_dirs, n_max_dirs)

    i = 0
    while i < n_files:
        fname = create_dirname(charset, root_dir)
        if not os.path.exists(fname):
            os.mkdir(fname)
            i += 1


def recursive_populate_directory_with_dirs(
        charset,
        root_dir,
        depth=5,
        **kwargs_populate_directory_with_dirs):

    dirs_to_populate = [root_dir, ]

    for _ in range(depth):
        update_dirs_to_populate = list()
        for one_dir in dirs_to_populate:
            populate_directory_with_dirs(
                charset,
                one_dir,
                **kwargs_populate_directory_with_dirs)
            for new_dirs in filter(os.path.isdir,
                                   os.listdir(one_dir)):
                update_dirs_to_populate.append(os.path.join(one_dir, new_dirs))
        dirs_to_populate = update_dirs_to_populate.copy()


def recursive_populate_directory_with_files(
        charset,
        root_dir,
        **kwargs_populate_directory_with_files):

    all_directories = map(
        lambda x: x[0],
        os.walk(root_dir))

    for one_dir in all_directories:
        populate_directory_with_files(
            charset,
            one_dir,
            **kwargs_populate_directory_with_files)


class MetaCreateSerializedTests(type):
    """Metaclas to create N number of tests.

    For each method of the object starting with 'test_' create N equal tests.

    """

    def __new__(mcs, name, bases, namespace):  # noqa
        test_serialization = []
        test_deletions = []
        for one_name in namespace:
            namespace_additions = dict()
            if one_name.startswith('test_'):
                for i in range(N):
                    namespace_additions[
                        one_name + '_' + str(i)] = namespace[one_name]
                test_serialization.append(namespace_additions)
                test_deletions.append(one_name)
        for one_namespace in test_serialization:
            namespace.update(one_namespace)
        for one_name in test_deletions:
            del namespace[one_name]
        return type.__new__(mcs, name, bases, namespace)


class TestBatchRenamer(unittest.TestCase, metaclass=MetaCreateSerializedTests):

    # Store original sys.argv because some tests override those to simulate CLI
    # calls.
    _original_sys_argv = sys.argv.copy()

    # Setup functions.
    def setUp(self):
        self._program_folder = tempfile.TemporaryDirectory()
        self.program_folder = os.path.abspath(self._program_folder.name)

        self.now = datetime.datetime.now()

    def setup_working_folder(self):
        # Create the working/renaming folder.
        self.working_folder = os.path.join(self.program_folder,
                                           'working_folder')
        os.mkdir(self.working_folder)

    def setup_config_folder(self):
        # Create the config folder.
        self.config_folder = os.path.abspath(os.path.join(
            self.program_folder,
            'config_folder'))
        os.mkdir(self.config_folder)
        # Create historyfile in config folder.
        self.historyfile = os.path.join(self.config_folder, 'historyfile.txt')
        os.mknod(self.historyfile)
        # Create excludepatternfile in config folder.
        self.excludepatternfile = os.path.join(self.config_folder,
                                               'excludepatternfile.txt')
        os.mknod(self.excludepatternfile)

    def setup_compliant_folder(self):

        self.setup_working_folder()

        self.compliant_folder = os.path.abspath(os.path.join(
            self.working_folder,
            'compliant_folder'))
        os.mkdir(self.compliant_folder)
        populate_directory_with_files(
            ALLOWED_CHARS,
            self.compliant_folder)

    def setup_non_compliant_folder(self):

        self.setup_working_folder()

        self.non_compliant_folder = os.path.abspath(os.path.join(
            self.working_folder,
            'non_compliant_folder'))
        os.mkdir(self.non_compliant_folder)
        populate_directory_with_files(
            NON_ALLOWED_CHARS,
            self.non_compliant_folder,)

    def tearDown(self):
        # os.system('tree ' + self.program_folder)
        self._program_folder.cleanup()
        sys.argv = self._original_sys_argv

    # Helper functions to construct 'real' command line invocations.
    def emulate_cli_arguments(
            self,
            arg_input=None,
            arg_revert=None,
            arg_historyfile=None,
            arg_excludepatternfile=None,
            arg_verbose=None,
            arg_prefixisomoddate=None,
            arg_dryrun=None,):
        # Intercept created arguments.
        new_sys_argv = []
        # Input.
        if arg_input is not None:
            new_sys_argv.append('--input')
            new_sys_argv.append(arg_input)
        # Input.
        if arg_revert is not None:
            new_sys_argv.append('--revert')
            new_sys_argv.append(arg_revert)
        # History file.
        if arg_historyfile is not None:
            new_sys_argv.append('--historyfile')
            new_sys_argv.append(arg_historyfile)
        # Exclude pattern file.
        if arg_excludepatternfile is not None:
            new_sys_argv.append('--excludepatternfile')
            new_sys_argv.append(arg_excludepatternfile)
        # Verbose.
        if arg_verbose is not None:
            new_sys_argv.append('--verbose')
        # Prefix with iso modification date.
        if arg_prefixisomoddate is not None:
            new_sys_argv.append('--prefixisomoddate')
        # Dry run.
        if arg_dryrun is not None:
            new_sys_argv.append('--dryrun')
        # Modify the system argv.
        sys.argv = [sys.argv[0], ] + new_sys_argv
        parser = brm.create_batch_renamer_parser()
        args = parser.parse_args()
        # Check those arguments again.
        brm.check_arguments(args)
        # Return the modified arguments.
        return args

    def get_path_representation_hash(self, path):
        m1 = hashlib.md5()
        representation = map(lambda x: '\n'.join((x[0], *x[1], *x[2])),
                             os.walk(path))
        representation = ''.join(representation)
        m1.update(representation.encode(encoding='utf8'))
        return m1.digest()


class TestBatchRenamerNormal(TestBatchRenamer):

    # TODO: remove me and put some real tests up.
    def test_has_changed(self):

        self.setup_config_folder()
        self.setup_non_compliant_folder()

        before_hash = self.get_path_representation_hash(
            self.non_compliant_folder)
        # Put null regex on exclude pattern file.
        # TODO: empty excludepatternfile should match no paths.
        with open(self.excludepatternfile, 'wt') as eptf:
            eptf.write('$^')
        args = self.emulate_cli_arguments(
            arg_input=self.non_compliant_folder,
            arg_historyfile=self.historyfile,
            arg_excludepatternfile=self.excludepatternfile,
            arg_verbose=True,
            arg_prefixisomoddate=None,
            arg_dryrun=None,)
        brm.main(args)
        after_hash = self.get_path_representation_hash(
            self.non_compliant_folder)
        self.assertNotEqual(before_hash, after_hash)

    def test_bogus_cli_calls(self):
        """Test wrong CLI calls."""
        # TODO: implement.
        pass

    def test_valid_cli_calls(self):
        """Test wrong CLI calls."""
        # TODO: implement.
        pass

    # Test primitive functions.
    def test_primitive_name(self):
        # Testing with allowed strings.
        for _, s in zip(range(N), create_random_string(ALLOWED_SYMBOLS)):
            with self.subTest(s=s):
                self.assertEqual(s, primitive_name(s))
        # Testing with non allowed strings.
        for _, s in zip(range(N),
                        create_random_string(
                            NON_ALLOWED_SYMBOLS,
                            min_len=2)):
            with self.subTest(s=s):
                self.assertEqual('_', primitive_name(s))
        # Testing with sequence of allowed strings with some underscore
        # sequence:

        def call_f(): return create_random_string(string.ascii_lowercase,
                                                  min_len=2, max_len=100)

        for s in (call_f() for x in range(N)):
            cutting_point = random.randint(1, len(s) - 1)
            s = s[:cutting_point] + '__' + s[cutting_point:]
            with self.subTest(s=s):
                self.assertEqual(s.replace('__', '_'),
                                 primitive_name(s))

    def test_add_trailing_number(self):
        # 10k max size takes some time.
        iterable_sizes = (10 ** x for x in range(1, 6))
        for size in iterable_sizes:
            for s in add_trailing_number(
                    ('a' for x in range(size)),
                    n=size):
                self.assertEqual(len(s), round(math.log(size, 10) + 2))

    def test_prefix_iso_mod_date(self):

        self.setup_compliant_folder()

        for file_path in filter(
                os.path.isfile,
                generate_folder_structure(self.compliant_folder)):
            with self.subTest(file_path):
                self.assertTrue(
                    os.path.basename(prefix_iso_mod_date(file_path))
                    .startswith(self.now.strftime('%Y%m%d_')))


class TestBatchRenamerRevert(TestBatchRenamer):

    def test_simple_revert(self):

        # Execute simple setup.
        self.setup_non_compliant_folder()
        self.setup_config_folder()

        # os.system('tree ' + self.program_folder)  # XXX

        # Compute first hash.
        first_hash = self.get_path_representation_hash(
            self.non_compliant_folder)

        # Populate needed config files.
        with open(self.excludepatternfile, 'wt') as eptf:
            eptf.write('$^')

        # Do a first run to rename the folder.
        args = self.emulate_cli_arguments(
            arg_input=self.non_compliant_folder,
            arg_historyfile=self.historyfile,
            arg_excludepatternfile=self.excludepatternfile)
        brm.main(args)

        second_hash = self.get_path_representation_hash(
            self.non_compliant_folder)

        # Execute the first assertion.
        self.assertNotEqual(first_hash, second_hash)

        # Restore renamed folder.
        args = self.emulate_cli_arguments(
            arg_input=None,
            arg_revert='last',
            arg_historyfile=self.historyfile,
            arg_excludepatternfile=self.excludepatternfile)
        brm.main(args)

        third_hash = self.get_path_representation_hash(
            self.non_compliant_folder)

        # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
        # os.system('tree ' + self.program_folder)  # XXX

        # Execute the first assertion.
        self.assertEqual(first_hash, third_hash)



if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBatchRenamer)
    unittest.TextTestRunner(verbosity=2).run(suite)
