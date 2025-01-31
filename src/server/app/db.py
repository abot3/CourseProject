import sqlite3
import os
import itertools
import click
import numpy as np
import pandas as pd

from flask import current_app, g
from flask.cli import with_appcontext
from . import csv_ingest
from . import sql_strings


def get_db():
    '''Get sqlite3 databse connection object.
    '''
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'],
                               detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    '''Close a sqlite3 databse connection object.
    '''
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    '''Create SQL tables from stored schema
    '''
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def do_readback():
    '''Readback rows from SQL tables to check schema.
  '''
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    SELECT *
    FROM
      corpus AS c
    ORDER BY
      c.id
    LIMIT 20;
  """)
    for row in cur.fetchall():
        print(row)

    cur.execute("""
    SELECT *
    FROM
      tags AS t
    ORDER BY
      t.id
    LIMIT 20;
  """)

    for row in cur.fetchall():
        keys = row.keys()
        r = tuple(row)
        print("keys: {}".format(keys))
        print("row: {}".format(r))


def read_all_doc_text_to_dataframe() -> pd.DataFrame:
    '''Retreive corpus doc text from SQL tables.

  Return a Pandas dataframe containing 1 row per document.
  '''
    db = get_db()
    df = pd.read_sql(sql_strings._SELECT_ALL_TEXT_DATA, db, index_col=None)
    print("read_all_doc_text_to_dataframe columns {}\n{}".format(
        df.columns, df))
    return df


# Limit -1 fetches all rows.
def read_all_cuisine_doc_text_to_dataframe(limit=-1) -> pd.DataFrame:
    '''Retreive corpus doc text from SQL tables. Only return rows
  containing keywords related to cuisines of interest.

  Return a Pandas dataframe containing 1 row per document.
  '''
    db = get_db()
    if limit == -1:
        df = pd.read_sql(sql_strings._SELECT_ALL_CUISINE_TEXT_DATA,
                         db,
                         index_col=None)
    else:
        df = pd.read_sql(sql_strings._SELECT_ALL_CUISINE_TEXT_DATA_WITH_LIMIT,
                         db,
                         params=[limit],
                         index_col=None)

    print("read_all_cuisine_doc_text_to_dataframe columns {}\n{}".format(
        df.columns, df))
    return df


def read_random_doc_text_to_dataframe(nrows=10) -> pd.DataFrame:
    '''Retreive corpus doc text from SQL tables.

  Select random documents from corpus using SQL.
  Limit the number of rows returned to nrows.

  Return a Pandas dataframe containing 1 row per document.
  '''
    db = get_db()
    df = pd.read_sql(sql_strings._SELECT_RANDOM_TEXT_DATA,
                     db,
                     params=[nrows],
                     index_col=None)
    print("read_random_doc_text_to_dataframe columns {}\n{}".format(
        df.columns, df))
    return df


def insert_data_into_db(pp_recipes_df: pd.DataFrame,
                        raw_recipes_df: pd.DataFrame):
    '''Clean and store text documents in SQL DB.

    Clean text fields in input dataframes. Each DataFrame row represents 1 doc.
    One row is created in DB for each row in the input DataFrames.
    '''
    db = get_db()
    cur = db.cursor()
    no_description = raw_recipes_df[(raw_recipes_df["description"] == "")
                                    | raw_recipes_df["description"].isnull()]
    no_name = raw_recipes_df[(raw_recipes_df["name"] == "")
                             | raw_recipes_df["name"].isnull() |
                             (raw_recipes_df["name"] == "NaN")]
    no_ingredients = raw_recipes_df[(raw_recipes_df["ingredients"] == "")
                                    | raw_recipes_df["ingredients"].isnull()]
    no_steps = raw_recipes_df[(raw_recipes_df["steps"] == "")
                              | raw_recipes_df["steps"].isnull()]
    no_ids = raw_recipes_df[(raw_recipes_df["id"].isnull()) |
                            (raw_recipes_df["id"].isna())]
    print("rows with no description {}\n{}".format(no_description.shape,
                                                   no_description.index))
    print("rows with no ids {}\n{}".format(no_ids.shape, no_ids.index))
    assert (no_ids.empty)
    raw_recipes_df.drop(labels=no_description.index, inplace=True)
    raw_recipes_df.drop(labels=no_name.index, inplace=True)
    raw_recipes_df.loc[no_ingredients.index, "ingredients"] = "no ingredients"
    raw_recipes_df.loc[no_steps.index, "steps"] = "no steps"
    raw_recipes_df.drop_duplicates("name", keep="first", inplace=True)
    raw_recipes_df.reset_index(inplace=True)
    rows = raw_recipes_df.loc[:, ["id", "name", "description"]]
    duplicated_names = raw_recipes_df.loc[raw_recipes_df["name"].duplicated(),
                                          ["id", "name", "description"]]
    duplicated_ids = raw_recipes_df.loc[raw_recipes_df["id"].duplicated(),
                                        ["id"]]
    assert (duplicated_ids.empty)
    print("duplicated_names {}".format(duplicated_names))
    print("duplicated ids {}".format(duplicated_ids))
    print("tags datatype as df {}\n{}".format(raw_recipes_df["tags"].dtypes,
                                              raw_recipes_df["tags"]))
    tags = raw_recipes_df["tags"].str.split(',')
    tags = tags.explode().str.strip('[]" \'\'.,')
    tags.drop_duplicates(keep="first", inplace=True)
    cur.executemany(sql_strings._INSERT_RAW_RECIPES_TAGS,
                    [(x, ) for x in tags.to_numpy(dtype=str).tolist()])
    db.commit()
    cur.executemany(sql_strings._INSERT_RAW_RECIPES_CORPUS,
                    rows.itertuples(index=False))
    db.commit()
    rows = raw_recipes_df.loc[:, [
        "id", "tags", "contributor_id", "steps", "description", "ingredients",
        "n_ingredients"
    ]]
    rows["id2"] = raw_recipes_df.loc[:, ["id"]]
    rows = rows.loc[:, [
        "id", "id2", "tags", "contributor_id", "steps", "description",
        "ingredients", "n_ingredients"
    ]]
    print("column names {}".format(rows.columns))
    duplicated_ids = rows.loc[rows["id"].duplicated(), ["id"]]
    assert (duplicated_ids.empty)
    duplicated_ids = rows.loc[rows["id2"].duplicated(), ["id2"]]
    assert (duplicated_ids.empty)
    # rows.insert(loc=1, column='id_repeat', value=rows["id"])
    print("rows before model insert t:{}\n{}".format(rows.dtypes, rows))
    print("rows as tuple {}".format(
        [x for x in itertools.islice(rows.itertuples(index=False), 10)]))
    cur.executemany(sql_strings._INSERT_RAW_RECIPES_MODELS,
                    rows.itertuples(index=False))
    db.commit()
    cur.execute(sql_strings._INSERT_DOC_TAGS)
    db.commit()

    # Readback the insertion results.
    do_readback()


def remove_n_path_components(n, path):
    '''Helper function to remove the last <n> elements from the file path.
    '''
    num = 0
    while num < n:
        path = os.path.dirname(path)
        yield path
        num += 1


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables.

    The freshly created tables are filled with data from the .csv files.
    The .csv files contain a list of ~230k recipes from food.com.

    This function can be run from the command line via `flask init-db`. See
    `click.command` for details.
    """
    path = [x for x in remove_n_path_components(3, current_app.root_path)][-1]
    *_, path = remove_n_path_components(3, current_app.root_path)
    path = os.path.join(path, "data/archive")
    pp_recipes_df = csv_ingest.IngestPpData(
        os.path.join(path, "PP_recipes.csv"))
    raw_recipes_df = csv_ingest.IngestRawData(
        os.path.join(path, "RAW_recipes.csv"))
    init_db()
    insert_data_into_db(pp_recipes_df, raw_recipes_df)
    click.echo('Initialized the database.')


def init_app(app):
    '''Called from flask_app.py.

  Adds the command line flag `flask init-db` to the Flask app.
  Adds a teardown callback that closes the DB connection.
  '''
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
