import sqlite3 as sql
import pandas as pd

class DB:
    def __init__(self):
        self.conn = sql.connect("data.sqlite")

    def has_table(self, name: str):
        master = pd.read_sql('select name from sqlite_master where type="table"', self.conn)
        return name in master["name"].values
    
    def execute(self, sql: str):
        rowid = -1
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            rowid = cur.lastrowid
        except Exception as e:
            sys.exit(f"could not execute sql: {sql} with \"{e}\"")
        return rowid
    
    def insert(self, table: str, df: pd.DataFrame):
        cols = ", ".join(df.columns)
        for i, row in df.iterrows():
            vals = []
            for c in df.columns:
                if row[c] is None:
                    vals.append("NULL")
                elif isinstance(row[c], str):
                    s = row[c].replace("'", "''").replace('"', '""')
                    vals.append(f'"{s}"')
                else:
                    vals.append(str(row[c]))
    
            vals = ", ".join(vals)
            self.__sql(f'insert into {table}({cols}) values ({vals})')
        return