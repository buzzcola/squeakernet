'''
Provides SqueakerNet with connectivity to a SQLite database for logging and stuff.
'''

import os
import sys
import sqlite3
import datetime
import dateutil.parser
from reading import Reading
from logcategory import LogCategory

db_filename = os.path.join(sys.path[0], 'squeakernet.db')

SQL_CREATE_DB = 'CREATE TABLE logs(id INTEGER PRIMARY KEY, date TEXT, category TEXT, message TEXT, reading NUMERIC)'
SQL_LOG = 'INSERT INTO logs(date, category, message, reading) VALUES (?, ?, ?, ?)'
SQL_SELECT_RECENT = 'SELECT id, date, category, message, reading FROM logs WHERE date BETWEEN datetime(\'now\', \'-6 days\') AND datetime(\'now\', \'localtime\') ORDER BY id DESC'
SQL_LAST_LOG = 'SELECT date, reading FROM logs WHERE category = ? ORDER BY date DESC LIMIT 1'
SQL_TODAYS_FEEDING = '''
SELECT start as date, reading FROM
    (SELECT :startofday as start, reading FROM logs WHERE category = 'WEIGHT' AND date LIKE :yesterday_pattern ORDER BY date DESC LIMIT 1)
UNION
SELECT date, reading FROM logs WHERE category = 'WEIGHT' AND date LIKE :today_pattern 
ORDER BY date'''

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DAY_FORMAT = '%Y-%m-%d'

def write_log(log_category, message, reading = 0.0):
    date = datetime.datetime.now().strftime(DATE_FORMAT)
    with _db() as db:
        db.cursor().execute(SQL_LOG, (date, log_category.name, message, reading))

def get_logs():
    with _db() as db:
        c = db.cursor()
        c.execute(SQL_SELECT_RECENT)
        return c.fetchall()

def get_last_log(log_category):
    with _db() as db:
        c = db.cursor()
        c.execute(SQL_LAST_LOG, (log_category.name,))
        result = c.fetchone()
    
    if result:
        return Reading(dateutil.parser.parse(result[0]), result[1])
    else:
        return None

def get_todays_feeding(offset = 0):
    with _db() as db:
        c = db.cursor()
        date = datetime.datetime.now() + datetime.timedelta(days = offset)        
        yesterday = date + datetime.timedelta(offset - 1)
        c.execute(SQL_TODAYS_FEEDING, {
            'startofday': date.strftime(DAY_FORMAT) + ' 00:00:00',
            'yesterday_pattern': yesterday.strftime(DAY_FORMAT) + '%',
            'today_pattern': date.strftime(DAY_FORMAT) + '%'
        })
        return c.fetchall()

def query(sql):
    with _db() as db:
        c = db.cursor()
        c.execute(sql)
        return c.fetchall()

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
