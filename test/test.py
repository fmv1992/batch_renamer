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
        lambda l: ''.join(random.choice(
            tuple(set_of_chars)) for x in range(l)),
        lenght_of_strings)
    return strings


def populate_folder(folder_path, symbol_set):
    """Helper function to populate folder with files.

    Helper function to populate folder with files drawing names from symbol
    set.

    Arguments:
        folder_path (str): folder path to populate.
        symbol_set (set): set of chars allowed to compose filename.

    """
    for file_name in create_string_from_set(symbol_set):
        file_path = os.path.join(folder_path, file_name)
        while os.path.exists(file_path):
            file_path = file_path + random.choice(tuple(symbol_set))
        os.mknod(file_path)
    return None


class BatchRenamerTest(unittest.TestCase):

    def setUp(self):
        self.program_folder = tempfile.TemporaryDirectory()
        # From a tuple of tuples generate a test structure and atributes:
        # ( (attr_name1, folder1), (attr_name2, folder2), ... )
        folder_structure = (
            ('config_folder', 'config'),
            ('test_folder', 'test'),
            ('excl_symbols_folder', 'excl_symbols'),
            ('compliant_names_folder', 'compl_names'))
        for attr_name, fname in folder_structure:
            setattr(self, attr_name,
                    os.path.abspath(
                        os.path.join(self.program_folder.name,
                                     fname)))
            os.mkdir(getattr(self, attr_name))
        self.now = datetime.datetime.now()
        # Initialize excl_symbols_folder.
        populate_folder(self.excl_symbols_folder, NON_ALLOWED_SYMBOLS)
        # Initialize compliant_names_folder.
        populate_folder(self.compliant_names_folder,
                        string.ascii_lowercase)

    def TearDown(self):
        self.program_folder.close()

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
        print()
        for size in iterable_sizes:
            for s in add_trailing_number(
                    create_string_from_set(set('a'),
                                           n=size,
                                           min_len=1,
                                           max_len=1),
                    n=size):
                self.assertEqual(len(s), round(math.log(size, 10) + 2))
            for i, s in enumerate(
                add_trailing_number(
                    create_string_from_set(set('a'),
                                           n=size,
                                           min_len=1,
                                           max_len=1))):
                if i == 0 or i == 1:
                    i = 2
                # TODO: fix this mathematical misunderstading: round and
                # math.floor or math.ceil do not work here
                # print(i)
                # print(s)
                # self.assertEqual(len(s), round(math.log(i, 10)) + 3)
                pass

    def test_prefix_iso_mod_date(self):
        # Test some dates.
        epoch_time = datetime.datetime(1970, 1, 1)
        # Test files created now.
        # Test files already with prefix.
        #   Which do have a correct prefix.
        #   Which do not have a correct prefix.
        for file_path in filter(
                os.path.isfile,
                generate_folder_structure(self.compliant_names_folder)):
            self.assertTrue(
                prefix_iso_mod_date(file_path).startswith(
                    now.strftime('%Y%m%d_')))



    def test_a(self):
        os.system('tree ' + self.program_folder.name)
        os.system('tree ' + self.program_folder.name)
        pass

    @property
    def verbosity(self):
        """Return the verbosity setting of the currently running unittest.

        This function 'scans' the

        Returns:
            int: the verbosity level.

            0 if this is the __main__ file
            1 if run with unittests module without verbosity (default in
            TestProgram)
            2 if run with unittests module with verbosity
        """
        frame = inspect.currentframe()
        # Scans frames from innermost to outermost for a TestProgram instance.
        # This python object has a verbosity defined in it.
        while frame:
            self = frame.f_locals.get('self')
            if isinstance(self, unittest.TestProgram):
                return self.verbosity
            # Proceed to one outer frame.
            frame = frame.f_back
        return 0


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(BatchRenamerTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # print(create_string_from_set('abcde', 100))
    # print(add_trailing_number(list('abcdefghijklmonopqrst')))
