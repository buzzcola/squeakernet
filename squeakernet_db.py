'''
Provides SqueakerNet with connectivity to a SQLite database for logging and stuff.
'''

import os
import sys
import sqlite3
import datetime
from enum import Enum

db_filename = os.path.join(sys.path[0], 'squeakernet.db')

SQL_CREATE_DB = 'CREATE TABLE logs(id INTEGER PRIMARY KEY, date TEXT, category TEXT, message TEXT, reading NUMERIC)'
SQL_LOG = 'INSERT INTO logs(date, category, message, reading) VALUES (?, ?, ?, ?)'
SQL_SELECT_ALL = 'SELECT id, date, category, message, reading FROM logs ORDER BY id DESC'
SQL_SELECT_CATEGORY = 'SELECT id, date, category, message, reading FROM logs WHERE category = ? ORDER BY id DESC'

DATE_FORMAT = '%Y-%m-%d %I:%M:%S'

def write_log(log_category, message, reading):
    date = datetime.datetime.now().strftime(DATE_FORMAT)
    with _db() as db:
        db.cursor().execute(SQL_LOG, (date, log_category.name, message, reading))

def get_logs(log_category = None):
    with _db() as db:
        c = db.cursor()
        if log_category:
            c.execute(SQL_SELECT_CATEGORY, (log_category.name,))
        else:
            c.execute(SQL_SELECT_ALL)
        return c.fetchall()

class LogCategory(Enum):
    FEED = 1
    SYSTEM = 2
    WEIGHT = 3

# this class lets us use the "with" keyword for quick easy SQL statements.
class _db():
    def __init__(self, check_existence = True):
        self.check_existence = check_existence

    def __enter__(self):
        self.db = _connect(self.check_existence)
        return self.db

    def __exit__(self, exception_type, exception_value, traceback):
        self.db.commit()
        self.db.close()

# connect to the db. Optionally create the DB (default).
def _connect(check_existence = True):
    if check_existence: _create_db_if_missing()
    return sqlite3.connect(db_filename)

# Create the database if it doesn't exist already.
def _create_db_if_missing():
    if os.path.isfile(db_filename): return
    with _db(False) as db:
        db.cursor().execute(SQL_CREATE_DB)
    write_log(LogCategory.SYSTEM, 'New database created.', 0)
