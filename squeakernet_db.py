'''
Provides SqueakerNet with connectivity to a SQLite database for logging and stuff.
'''

import os, sys, sqlite3, datetime

db_filename = os.path.join(sys.path[0], 'squeakernet.db')

sql_create_db = 'CREATE TABLE logs(id INTEGER PRIMARY KEY, date TEXT, message TEXT, reading NUMERIC)'
sql_log = 'INSERT INTO logs(date, message, reading) VALUES (?, ?, ?)'
sql_select_all = 'SELECT id, date, message, reading FROM logs ORDER BY id DESC'

date_format = '%Y-%m-%d %I:%M:%S'

def writeLog(message, reading):
    date = datetime.datetime.now().strftime(date_format)
    with _db() as db:
        db.cursor().execute(sql_log, (date, message, reading))

def getLogs():
    with _db() as db:
        c = db.cursor()
        c.execute(sql_select_all)        
        return c.fetchall()

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
    if check_existence: _createDbIfMissing()
    return sqlite3.connect(db_filename)

# Create the database if it doesn't exist already.
def _createDbIfMissing():
    if os.path.isfile(db_filename): return
    with _db(False) as db:
        db.cursor().execute(sql_create_db)