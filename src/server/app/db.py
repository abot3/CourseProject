import sqlite3
import os

import click
from flask import current_app, g
from flask.cli import with_appcontext
from . import csv_ingest


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'],
                               detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def remove_n_path_components(n, path):
    num = 0
    while num < n:
        path = os.path.dirname(path)
        yield path
        num += 1


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    path = [x for x in remove_n_path_components(3, current_app.root_path)][-1]
    *_, path = remove_n_path_components(3, current_app.root_path)
    path = os.path.join(path, "data/archive")
    pp_recipes_df = csv_ingest.IngestPpData(
        os.path.join(path, "PP_recipes.csv"))
    raw_recipes_df = csv_ingest.IngestRawData(
        os.path.join(path, "RAW_recipes.csv"))
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
