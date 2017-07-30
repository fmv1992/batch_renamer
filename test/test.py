import string
import random
import os
import unittest
import tempfile
import datetime
import math

from batch_renamer.batch_renamer import primitive_name, generate_folder_structure, add_trailing_number, prefix_iso_mod_date  # noqa


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

    call_f = lambda: create_filename(
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
        kwargs_create_file_extension=dict(),
        kwargs_create_random_string=dict()):

    call_f = lambda: create_dirname(root_dir, **kwargs_create_random_string)

    for dirname in (call_f() for x in range(
            random.randint(n_min_dirs, n_max_dirs))):
        # print(dirname)
        os.mkdir(dirname)

    return None


def recursive_populate_directory_with_dirs():
    pass


def recursive_populate_directory_with_files():
    # Ensure in every node.
    pass


class TestBatchRenamer(unittest.TestCase):

    def setUp(self):
        self._program_folder = tempfile.TemporaryDirectory()
        self.program_folder = os.path.abspath(self._program_folder.name)
        self.config_folder = os.path.abspath(os.path.join(
            self.program_folder,
            'config_folder'))
        os.mkdir(self.config_folder)
        self.compliant_folder = os.path.abspath(os.path.join(
            self.program_folder,
            'compliant_folder'))
        os.mkdir(self.compliant_folder)
        self.non_compliant_folder = os.path.abspath(os.path.join(
            self.program_folder,
            'non_compliant_folder'))
        os.mkdir(self.non_compliant_folder)
        # TODO: why now?
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

    def tearDown(self):
        self._program_folder.cleanup()

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

        call_f = lambda: create_random_string(string.ascii_lowercase,
                                              min_len=2, max_len=100)

        for s in (call_f() for x in range(N)):
            cutting_point = random.randint(1, len(s) - 1)
            s = s[:cutting_point] + '__' + s[cutting_point:]
            with self.subTest(s=s):
                self.assertEqual(s.replace('__', '_'),
                                 primitive_name(s))

    def test_add_trailing_number(self):
        # 10k max size takes some time.
        iterable_sizes = (10 ** x for x in range(1, 5))
        for size in iterable_sizes:
            for s in add_trailing_number(
                 create_random_string(set('a'),
                                      min_len=1,
                                      max_len=1),
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
