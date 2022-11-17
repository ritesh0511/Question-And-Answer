import sqlite3

import click
import psycopg2
from flask import current_app, g
from psycopg2.extras import DictCursor

# def connect_db():
#     conn = sqlite3.connect('qa.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# def get_db():
#     if 'db' not in g:
#         g.db = connect_db()
#     return g.db

# def init_db():
#     db = get_db()

#     with current_app.open_resource('schema.sql') as f:
#         db.executescript(f.read().decode('utf8'))
#     db.commit()
#     db.close()



def connect_db():
    conn = psycopg2.connect('postgres://bgiswqmjzwteqz:d72b5fbd07b542813789f62657471ea689bdf9fa1497703144c2b101c45bdd95@ec2-35-173-91-114.compute-1.amazonaws.com:5432/d7jmp1a2jp49a4',cursor_factory=DictCursor)
    conn.autocommit = True
    return conn

def get_db():
    db = connect_db()
    cur = db.cursor()
    if 'postgres_db_conn' not in g:
        g.postgres_db_conn = cur
    return g.postgres_db_conn

def init_db():
    db = connect_db()
    cur = db.cursor()
    cur.execute(open('schema.sql','r').read())
    cur.close()
    db.close()


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the Database.')

def init_app(app):
    app.cli.add_command(init_db_command)