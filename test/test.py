import random
import math
import string
import os
import tempfile
import inspect
import datetime
import unittest
from batch_renamer.batch_renamer import primitive_name, generate_folder_structure, add_trailing_number, prefix_iso_mod_date  # noqa

# pylama:ignore=D100,D101,D102

PATH_RESERVED_SYMBOLS = set(('\\', '/'))
ALLOWED_SYMBOLS = set(('_', '.'))
NON_ALLOWED_SYMBOLS = (set(string.punctuation)
                       - (ALLOWED_SYMBOLS | PATH_RESERVED_SYMBOLS))

N = 500  # Number of strings in each folder.


def create_string_from_set(set_of_chars,
                           n=100,
                           min_len=10,
                           max_len=100):
    """Return a map of n strings between min and max lenght."""
    lenght_of_strings = (random.randint(min_len, max_len) for x in range(n))
    strings = map(
        lambda len_of_str: ''.join(
            random.choice(tuple(set_of_chars)) for x in range(len_of_str)),
        lenght_of_strings)
    return strings


def populate_folder(folder_path,
                    symbol_set,
                    recursive=False,
                    rec_branching_probability=0.5,
                    rec_initial_child_folders=5):
    """Helper function to populate folder with files.

    Helper function to populate folder with files drawing names from symbol
    set.

    Arguments:
        folder_path (str): folder path to populate.
        symbol_set (set): set of chars allowed to compose filename.

    """
    # # Create folders recursively.
    # if recursive:
    #     for _, dir_name in enumerate(create_string_from_set(symbol_set)):
    #         file_path = os.path.join(folder_path, file_name)
    #         while os.path.exists(dir_name):
    #             dir_name = dir_name + random.choice(tuple(symbol_set))
    #         os.mkdir(file_path)

    # Populate folders recursively.
    for file_name in create_string_from_set(symbol_set):
        file_path = os.path.join(folder_path, file_name)
        while os.path.exists(file_path):
            file_path = file_path + random.choice(tuple(symbol_set))
        os.mknod(file_path)
    return None


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
        populate_folder(self.non_compliant_folder, NON_ALLOWED_SYMBOLS)
        # Initialize compliant_names_folder.
        populate_folder(self.compliant_folder,
                        string.ascii_lowercase)

    def tearDown(self):
        self._program_folder.cleanup()

    def test_primitive_name(self):
        # Testing with allowed strings.
        for s in create_string_from_set(string.ascii_lowercase,
                                        n=N):
            with self.subTest(s=s):
                self.assertEqual(s, primitive_name(s))
        # Testing with non allowed strings.
        for s in create_string_from_set(NON_ALLOWED_SYMBOLS,
                                        n=N,
                                        min_len=2):
            with self.subTest(s=s):
                self.assertEqual('_', primitive_name(s))
        # Testing with sequence of allowed strings with some underscore
        # sequence:
        for s in create_string_from_set(string.ascii_lowercase,
                                        n=N,
                                        min_len=2,
                                        max_len=100):
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
                    create_string_from_set(set('a'),
                                           n=size,
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
    suite = unittest.TestLoader().loadTestsFromTestCase(BatchRenamerTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # print(create_string_from_set('abcde', 100))
    # print(add_trailing_number(list('abcdefghijklmonopqrst')))
