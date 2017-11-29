import basics
import os
import test
import unittest

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

    def test_temp_workspace(self):
        pass


if __name__ == '__main__':
    unittest.main()
