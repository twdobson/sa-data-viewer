import tempfile
import pandas as pd

from typing import Dict


def create_label_value_pairs_from_series(series):
    return [
        {'label': value, 'value': value}
        for value
        in series
    ]


def read_sql_to_pandas(sql_query, db):
    """
    https://towardsdatascience.com/optimizing-pandas-read-sql-for-postgres-f31cd7f707ab
    """

    return read_sql_tmpfile(
        query=sql_query,
        db=db
    )


def read_sql_tmpfile(query, db):
    with tempfile.TemporaryFile() as tmpfile:
        copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
            query=query, head="HEADER"
        )
        conn = db.get_engine().raw_connection()
        cur = conn.cursor()
        cur.copy_expert(copy_sql, tmpfile)
        tmpfile.seek(0)
        df = pd.read_csv(tmpfile)
        return df


def read_sql_inmem_uncompressed_to_pandas(query, db):
    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
        query=query, head="HEADER"
    )
    conn = db.get_engine().raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    df = pd.read_csv(store)
    return df
