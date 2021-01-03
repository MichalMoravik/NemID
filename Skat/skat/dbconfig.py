import sqlite3
from flask import g
from skat import app

SKATDATABASE = 'skat/skat.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SKATDATABASE)
        db.row_factory = sqlite3.Row
        # turn foreign keys on, to make constraints
        db.cursor().execute("PRAGMA foreign_keys=ON")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()