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
PATH_RESERVED_SYMBOLS = set(('\\', '/'))
ALLOWED_SYMBOLS = set(('_', '.'))
NON_ALLOWED_SYMBOLS = (set(string.punctuation)
                       - (ALLOWED_SYMBOLS | PATH_RESERVED_SYMBOLS))
N = 500  # Number of strings in each folder.


def create_random_string(allowed_chars=string.ascii_lowercase,
                         min_len=10,
                         max_len=100):
    return ''.join(random.choice(tuple(allowed_chars)) for x in
                   range(random.randint(min_len, max_len)))


def create_file_extension(extension=None):
    if extension is None:
        all_extensions = ('txt', 'mp3', 'py', 'tar.xz', '.tar', )
        extension = random.choice(all_extensions)
    return extension


def create_filename(
        root_dir,
        include_extension=False,
        kwargs_create_file_extension=dict(),
        kwargs_create_random_string=dict()):
    if include_extension:
        extension = create_file_extension(**kwargs_create_file_extension)
    else:
        extension = ''
    return os.path.join(
        root_dir,
        create_random_string(**kwargs_create_random_string)
        + extension)


def create_dirname(root_dir, kwargs_create_random_string=dict()):
    return os.path.join(root_dir,
                        create_random_string(**kwargs_create_random_string))


def populate_directory_with_files(
        root_dir,
        include_extension=False,
        n_min_files=5,
        n_max_files=10,
        kwargs_create_file_extension=dict(),
        kwargs_create_random_string=dict()):

    def call_f(): return create_filename(
        root_dir,
        include_extension=include_extension,
        kwargs_create_file_extension=kwargs_create_file_extension,
        kwargs_create_random_string=kwargs_create_random_string)

    for fname in (call_f() for x in range(
            random.randint(n_min_files, n_max_files))):
        # print(fname)
        os.mknod(fname)

    return None


def populate_directory_with_dirs(
        root_dir,
        n_min_dirs=5,
        n_max_dirs=10,
        kwargs_create_random_string=dict()):

    def call_f(): return create_dirname(
        root_dir,
        kwargs_create_random_string=kwargs_create_random_string)

    for dirname in (call_f() for x in range(
            random.randint(n_min_dirs, n_max_dirs))):
        # TODO: need to compensate this case on the else part.
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        else:
            pass

    return None


def recursive_populate_directory_with_dirs(
        root_dir,
        max_depth=5,
        n_min_dirs=0,
        n_max_dirs=3,
        kwargs_create_random_string=dict()):
    populate_dirs = [root_dir, ]
    for i in range(max_depth):
        new_dirs = list()
        for d in populate_dirs:
            branching = random.randint(n_min_dirs, n_max_dirs)
            populate_directory_with_dirs(
                d,
                branching,
                branching,
                kwargs_create_random_string=kwargs_create_random_string)
            new_dirs += list(map(
                lambda x: os.path.join(d, x),
                filter(os.path.isdir,
                       map(lambda x: os.path.join(d, x),
                           os.listdir(d)))))
            populate_dirs = new_dirs.copy()


def recursive_populate_directory_with_files():
    # Ensure in every node.
    pass


class TestBatchRenamer(unittest.TestCase):

    # Store original sys.argv because some tests override those to simulate CLI
    # calls.
    _original_sys_argv = sys.argv.copy()

    def setUp(self):
        self._program_folder = tempfile.TemporaryDirectory()
        self.program_folder = os.path.abspath(self._program_folder.name)
        # Create the config folder.
        self.config_folder = os.path.abspath(os.path.join(
            self.program_folder,
            'config_folder'))
        # TODO: Populate the config folder.
        os.mkdir(self.config_folder)
        self.compliant_folder = os.path.abspath(os.path.join(
            self.program_folder,
            'compliant_folder'))
        os.mkdir(self.compliant_folder)
        self.non_compliant_folder = os.path.abspath(os.path.join(
            self.program_folder,
            'non_compliant_folder'))
        os.mkdir(self.non_compliant_folder)
        self.recursively_pop_dir = os.path.abspath(os.path.join(
            self.program_folder,
            'recursively_pop_dir'))
        os.mkdir(self.recursively_pop_dir)
        # TODO: May help with 'test_prefix_iso_mod_date'.
        self.now = datetime.datetime.now()
        # Initialize excl_symbols_folder.
        populate_directory_with_files(
            self.non_compliant_folder,
            kwargs_create_random_string={'allowed_chars': NON_ALLOWED_SYMBOLS})
        # Initialize compliant_names_folder.
        populate_directory_with_files(
            self.compliant_folder,
            kwargs_create_random_string={
                'allowed_chars': string.ascii_lowercase})
        # Initialize recursively populated directory.
        recursive_populate_directory_with_dirs(
            self.recursively_pop_dir,
            kwargs_create_random_string={
                'min_len': 1,
                'max_len': 5})
        # Create historyfile.
        self.historyfile = os.path.join(self.config_folder, 'historyfile.txt')
        os.mknod(self.historyfile)
        # Create excludepatternfile.
        self.excludepatternfile = os.path.join(self.config_folder,
                                               'excludepatternfile.txt')
        os.mknod(self.excludepatternfile)

    def tearDown(self):
        # os.system('tree ' + self.program_folder)
        self._program_folder.cleanup()
        sys.argv = self._original_sys_argv

    # Helper functions to construct 'real' command line invocations.
    def emulate_cli_arguments(
            self,
            arg_input=None,
            arg_historyfile=None,
            arg_excludepatternfile=None,
            arg_verbose=None,
            arg_prefixisomoddate=None,
            arg_dryrun=None,):
        # Intercept created arguments.
        new_sys_argv = []
        # Input.
        new_sys_argv.append('--input')
        new_sys_argv.append(arg_input)
        # History file.
        new_sys_argv.append('--historyfile')
        new_sys_argv.append(arg_historyfile)
        # Exclude pattern file.
        new_sys_argv.append('--excludepatternfile')
        new_sys_argv.append(arg_excludepatternfile)
        # Verbose.
        if arg_verbose:
            new_sys_argv.append('--verbose')
        # Prefix with iso modification date.
        if arg_prefixisomoddate:
            new_sys_argv.append('--prefixisomoddate')
        # Dry run.
        if arg_dryrun:
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

    # TODO: remove me and put some real tests up.
    def test_has_changed(self):
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
        for file_path in filter(
                os.path.isfile,
                generate_folder_structure(self.compliant_folder)):
            with self.subTest(file_path):
                self.assertTrue(
                    os.path.basename(prefix_iso_mod_date(file_path))
                    .startswith(self.now.strftime('%Y%m%d_')))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBatchRenamer)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # print(create_string_from_set('abcde', 100))
    # print(add_trailing_number(list('abcdefghijklmonopqrst')))
