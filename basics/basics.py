''' Basic utilities for doing analysis in Python '''

import csv
import collections

class NamedTupleReader():
    ''' Like csv.DictReader, but returns namedtuples instead.

        Key differences between NamedTupleReader and DictReader:

          - Since the fieldnames of the RowTuple type cannot change,
            it is an error to try and set the "fieldnames" property.

          - Since the number of fields in the RowTuple cannot change,
            there is no 'restkey'. If a row in the csv file has too
            many values, all extra values are stuffed in the last slot
            of the tuple:

                >> f = open('test.csv')
                >> f.read()
                'one,two,three,four'
                >> f.seek(0)
                >> next(NamedTupleReader(f, ['first', 'other']))
                RowTuple(first='one', other=['two', 'three', 'four'])

        Other notes:
          - Like csv.DictReader, but unlike a basic csv.reader, the
            NamedTupleReader will skip blank rows.
    '''
    def __init__(self, filename, fieldnames=None, restval=None, dialect='excel', *arg, **kwargs):
        self.dialect = dialect
        self.restval = restval
        self.reader  = csv.reader(filename, dialect, *arg, **kwargs)
        if fieldnames is None:
            fieldnames = next(self.reader)
        self.RowTuple = collections.namedtuple('RowTuple', fieldnames)
        self.line_num = self.reader.line_num

    @property
    def fieldnames(self):
        return list(self.RowTuple._fields)

    def __iter__(self):
        return self

    def __next__(self):
        row = []
        while not row:
            row = next(self.reader)
        self.line_num = self.reader.line_num
        lr, lf = len(row), len(self.RowTuple._fields)
        if lr < lf:
            row.extend([self.restval] * (lf-lr))
        elif lr > lf:
            row = row[:lf-1] + [row[lf-1:]]
        return self.RowTuple._make(row)
