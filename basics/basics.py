''' Basic utilities for doing analysis in Python '''

import collections
import contextlib
import csv
import functools
import logging
import os
import shutil
import tempfile
from pathlib import Path

#-----------------------------------------------------------------------
# CSV Utilities
#-----------------------------------------------------------------------
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
    def __init__(self, filename, fieldnames=None, restval=None, dialect='excel', *args, **kwargs):
        self.dialect = dialect
        self.restval = restval
        self.rename  = kwargs.pop('rename', False) # Pop before passing to reader
        self.reader  = csv.reader(filename, dialect, *args, **kwargs)
        if fieldnames is None:
            fieldnames = next(self.reader)
        self.RowTuple = collections.namedtuple('RowTuple', fieldnames, rename=self.rename)
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

class excel_stripped(csv.excel):
    ''' Like the default excel dialect, but skips leading whitespace '''
    skipinitialspace = True
csv.register_dialect("excel-strip", excel_stripped)

class excel_tab_stripped(csv.excel_tab):
    ''' Like the default excel_tab dialect, but skips leading whitespace '''
    skipinitialspace = True
csv.register_dialect("excel-tab-strip", excel_tab_stripped)

class unix_stripped(csv.unix_dialect):
    ''' Like the default unix dialect, but skips leading whitespace '''
    skipinitialspace = True
csv.register_dialect("unix-strip", unix_stripped)


#-----------------------------------------------------------------------
# Temporary Directory Management
#-----------------------------------------------------------------------
@contextlib.contextmanager
def temp_workspace():
    ''' Create/chdir to temp directory on entry; restore cwd and cleanup on exit. '''
    home = Path.cwd()
    with tempfile.TemporaryDirectory() as temp:
        try:
            os.chdir(temp)
            yield Path(temp)
        finally:
            os.chdir(home)

def tempdir(*args):
    ''' Decorator to run a function in a clean temporary directory.

    This decorator can be applied to a function when that function needs to run
    in a temporary directory isolated from the rest of the filesystem. The
    decorator creates a temporary directory, chdir's into it, calls the wrapped
    function, and then deletes the temporary workspace after chdir'ing back to
    the start location.

    In some cases (e.g. debugging), immeadiately deleting the workspace is
    undesirable. This can be disabled by passing the 'debug' or 'noclean'
    string (actually, any argument will do) to the decorator:

        @tempdir('debug')
        def my_function():
            ...etc.

    When in debug mode, the temporary directory is created in the current
    working directory and is not cleaned up after the function returns. The
    directory is deterministically named based on the functons __qualname__.
    If this test directory exists before the function is called (e.g. from a
    previous debug run) it is deleted and re-created. Note that when running in
    debug mode, race conditions and naming collisions are possible.

    NOTE:
        Implementation based on https://stackoverflow.com/questions/3931627

    '''
    def _tempdir(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if debug:
                # Call from new subdirectory; no cleanup
                home = Path.cwd()
                temp = Path(f'DEBUG_{func.__qualname__}')
                if temp.exists():
                    shutil.rmtree(temp)
                temp.mkdir()
                try:
                    os.chdir(temp)
                    return func(*args, **kwargs)
                finally:
                    os.chdir(home)
            else:
                # Call from isolated workspae
                with temp_workspace():
                    return func(*args, **kwargs)
        return wrapper

    if len(args) == 1 and callable(args[0]):
        debug = False
        return _tempdir(args[0])
    else:
        debug = True
        return _tempdir


#-----------------------------------------------------------------------
# Logging
#-----------------------------------------------------------------------
def nologging(func):
    ''' Decorator to disable logging from a function or method '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.disable(logging.ERROR)
            return func(*args, **kwargs)
        finally:
            logging.disable(logging.NOTSET)
    return wrapper


#-----------------------------------------------------------------------
# Testing
#-----------------------------------------------------------------------
#TODO: Subclass unittest.TestCase w/ asserts for comparing files/directories
