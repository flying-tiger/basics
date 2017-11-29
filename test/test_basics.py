import basics
import os
import test
import unittest
from pathlib import Path

class TestNamedTupleReader(unittest.TestCase):
    """ Tests for NamedTupleReader """

    def test_simple_read(self):
        with open(test.data_dir/'numbers.csv') as csvfile:
            next(csvfile) # Skip header
            fieldnames = ['a','b','c']
            reader = basics.NamedTupleReader(csvfile, fieldnames)
            self.assertEqual(reader.fieldnames, fieldnames)
            row = next(reader)
            self.assertEqual(row.a, '11')
            self.assertEqual(row.b, '12')
            self.assertEqual(row.c, '13')
            self.assertEqual(reader.line_num, 1)

    def test_fieldnames_from_header(self):
        with open(test.data_dir/'numbers.csv') as csvfile:
            reader = basics.NamedTupleReader(csvfile)
            self.assertEqual(reader.fieldnames, ['col1', 'col2', 'col3'])
            self.assertTrue(reader.line_num, 1)
            row = next(reader)
            self.assertEqual(row.col1, '11')
            self.assertEqual(row.col2, '12')
            self.assertEqual(row.col3, '13')
            self.assertEqual(reader.line_num, 2)

    def test_too_many_fields(self):
        with open(test.data_dir/'numbers.csv') as csvfile:
            next(csvfile) # Skip header
            fieldnames = ['col1','col2','col3','extra_field']
            reader = basics.NamedTupleReader(csvfile, fieldnames)
            row = next(reader)
            self.assertEqual(row.col1, '11')
            self.assertEqual(row.col2, '12')
            self.assertEqual(row.col3, '13')
            self.assertEqual(row.extra_field, None)

    def test_too_few_fields(self):
        with open(test.data_dir/'numbers.csv') as csvfile:
            next(csvfile) # Skip header
            fieldnames = ['col1','the_rest']
            reader = basics.NamedTupleReader(csvfile, fieldnames)
            row = next(reader)
            self.assertEqual(row.col1, '11')
            self.assertEqual(row.the_rest, ['12', '13'])

    def test_additional_dialects(self):
        with open(test.data_dir/'whitespace.csv') as csvfile:
            reader = basics.NamedTupleReader(csvfile, dialect='unix-strip')
            row = next(reader)
            self.assertEqual(row.first_name, 'Jane')
            self.assertEqual(row.last_name,  'Doe')
            self.assertEqual(row.age,        '42')

    def test_rename_fields(self):
        with open(test.data_dir/'whitespace.csv') as csvfile:
            # Try using the first row of ada a columns headers. This fails
            # because the value in the age column, '42', is not a valid python
            # identifier and cannot be used as a tuple field name.
            next(csvfile) # Skip header
            with self.assertRaises(ValueError):
                basics.NamedTupleReader(csvfile, skipinitialspace=True)

        with open(test.data_dir/'whitespace.csv') as csvfile:
            # Try the same thing, but allow renaming. This will use '_2' as a
            # field names instead of '42'.
            next(csvfile) # Skip header
            reader = basics.NamedTupleReader(csvfile, rename=True, skipinitialspace=True)
            self.assertEqual(reader.fieldnames, ['Jane', 'Doe', '_2'])

class TestTempWorkspace(unittest.TestCase):
    """ Tests for temp_workspace """

    def test_temp_workspace(self):
        """ Verify create/enter/exit/delete a temp directory """
        start = Path.cwd()
        with basics.temp_workspace() as temp:
            self.assertTrue(temp.samefile(Path.cwd()))
            self.assertFalse(temp.samefile(start))
        self.assertTrue(start.samefile(Path.cwd()))
        self.assertFalse(temp.exists())

class TestTempDir(unittest.TestCase):
    """ Test the @tempdir decorator """

    def test_normal_mode(self):
        """ Verify function is run in temp directory that is cleaned up """
        @basics.tempdir
        def where_am_i():
            return Path.cwd()

        start  = Path.cwd()
        rundir = where_am_i()
        self.assertNotEqual(str(rundir), str(start))
        self.assertFalse(rundir.exists())

    def test_debug_mode(self):
        """ Test excution in local subdirectory w/o cleanup """
        @basics.tempdir("debug")
        def where_am_i():
            return Path.cwd()

        with basics.temp_workspace():
            start  = Path.cwd()
            rundir = where_am_i()
            self.assertTrue(rundir.exists())
            self.assertTrue(rundir.parent.samefile(start))

            # Verify delete/recreate debug directory when function is re-run
            canary = Path(rundir, 'canary.txt')
            canary.write_text('now you see me...')
            rundir2 = where_am_i()
            self.assertEqual(str(rundir), str(rundir2))
            self.assertFalse(canary.exists())

if __name__ == '__main__':
    unittest.main()
