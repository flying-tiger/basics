import basics
import env
import os
import unittest


def testfile(name):
    ''' Returns full path to a file in test/data directory '''
    return os.path.join(env.test_root, 'data', name)


class TestNamedTupleReader(unittest.TestCase):

    def test_simple_read(self):
        with open(testfile('numbers.csv')) as csvfile:
            fieldnames = ['a','b','c']
            reader = basics.NamedTupleReader(csvfile, fieldnames)
            self.assertEqual(reader.fieldnames, fieldnames)
            next(reader) # Skip header
            row = next(reader)
            self.assertEqual(row.a, '11')
            self.assertEqual(row.b, '12')
            self.assertEqual(row.c, '13')
            self.assertEqual(reader.line_num, 2)

    def test_fieldnames_from_header(self):
        with open(testfile('numbers.csv')) as csvfile:
            reader = basics.NamedTupleReader(csvfile)
            self.assertEqual(reader.fieldnames, ['col1', 'col2', 'col3'])
            self.assertTrue(reader.line_num, 1)
            row = next(reader)
            self.assertEqual(row.col1, '11')
            self.assertEqual(row.col2, '12')
            self.assertEqual(row.col3, '13')
            self.assertEqual(reader.line_num, 2)

    def test_too_many_fields(self):
        with open(testfile('numbers.csv')) as csvfile:
            fieldnames = ['col1','col2','col3','extra_field']
            reader = basics.NamedTupleReader(csvfile, fieldnames)
            next(reader) # Skip header
            row = next(reader)
            self.assertEqual(row.col1, '11')
            self.assertEqual(row.col2, '12')
            self.assertEqual(row.col3, '13')
            self.assertEqual(row.extra_field, None)

    def test_too_few_fields(self):
        with open(testfile('numbers.csv')) as csvfile:
            fieldnames = ['col1','the_rest']
            reader = basics.NamedTupleReader(csvfile, fieldnames)
            next(reader) # Skip header
            row = next(reader)
            self.assertEqual(row.col1, '11')
            self.assertEqual(row.the_rest, ['12', '13'])


if __name__ == '__main__':
    unittest.main()
