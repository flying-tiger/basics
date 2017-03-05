''' Basic utilities for doing analysis in Python '''

import csv
import collections

class NamedTupleReader():
    ''' Like csv.DictReader, but returns namedtuples instead.

        Key differences between NamedTupleReader and DictReader:
          - It is an error if number of columns in a row != len(fieldnames).
          - Prettier syntax!

        Other notes:
          - Like DictReader, NamedTupleReader will skip blank rows.
    '''
    def __init__(self, filename, fieldnames, dialect='excel', *arg, **kwargs):
        self.reader = csv.reader(filename, dialect, *arg, **kwargs)
        self.RowTuple = collections.namedtuple('RowTuple', fieldnames)
        self.line_num = self.reader.line_num

    @property
    def fieldnames(self):
        return list(self.RowTuple._fields)

    def __iter__(self):
        return self

    def __next__(self):
        row = []
        while row == []:
            row = next(self.reader)
        self.line_num = self.reader.line_num
        return self.RowTuple._make(row)
