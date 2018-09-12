'''
Provides SqueakerNet with connectivity to a SQLite database for logging and stuff.
'''

import os
import sys
import sqlite3
import datetime
import dateutil.parser
from enum import Enum
from WeightReading import *

db_filename = os.path.join(sys.path[0], 'squeakernet.db')

SQL_CREATE_DB = 'CREATE TABLE logs(id INTEGER PRIMARY KEY, date TEXT, category TEXT, message TEXT, reading NUMERIC)'
SQL_LOG = 'INSERT INTO logs(date, category, message, reading) VALUES (?, ?, ?, ?)'
SQL_SELECT_ALL = 'SELECT id, date, category, message, reading FROM logs ORDER BY id DESC'
SQL_SELECT_CATEGORY = 'SELECT id, date, category, message, reading FROM logs WHERE category = ? ORDER BY id DESC'
SQL_LAST_FEED = "SELECT MAX(date) FROM logs WHERE category = 'FEED'"
SQL_LAST_WEIGHT = "SELECT date, reading FROM logs WHERE category = 'WEIGHT' ORDER BY date DESC LIMIT 1"

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def write_log(log_category, message, reading = 0.0):
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

def get_last_feed():
    with _db() as db:
        c = db.cursor()
        c.execute(SQL_LAST_FEED)
        result = c.fetchone()
    
    if result: 
        return dateutil.parser.parse(result[0])
    else:
        return None

def get_last_weight():
    with _db() as db:
        c = db.cursor()
        c.execute(SQL_LAST_WEIGHT)
        result = c.fetchone()
    
    if result:
        return WeightReading(dateutil.parser.parse(result[0]), result[1])
    else:
        return None

class LogCategory(Enum):
    FEED = 1
    SYSTEM = 2
    WEIGHT = 3

# this class lets us use the "with" keyword for SQL with less ceremony.
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
