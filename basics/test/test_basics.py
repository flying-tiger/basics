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
            self.assertTrue(reader.fieldnames == fieldnames)
            row = next(reader)
            self.assertTrue(row.a == '11')
            self.assertTrue(row.b == '12')
            self.assertTrue(row.c == '13')
            self.assertTrue(reader.line_num == 1)


if __name__ == '__main__':
    unittest.main()
