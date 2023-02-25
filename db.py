import sqlite3

import click
# import psycopg2
from flask import current_app, g
# from psycopg2.extras import DictCursor

def connect_db():
    conn = sqlite3.connect('qa.db')
    
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    if 'db' not in g:
        g.db = connect_db()
    return g.db

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    db.commit()
    db.close()


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the Database.')

def init_app(app):
    app.cli.add_command(init_db_command)