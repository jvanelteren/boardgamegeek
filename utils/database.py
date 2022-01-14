import pandas as pd
import sqlite3
from functools import reduce
import operator
from IPython.display import display_html 


# PRAGMA table_info(reviews);"""
# PRAGMA foreign_keys = ON;


class DB():
    def __init__(self, filepath):
        self.conn = sqlite3.connect(filepath)
        print(self.count())
        
    def __call__(self, sql):
        res = self.conn.execute(sql)
        return list(res.fetchall())
            
    
    def do(self, sql):
        # identical to calling the object
        return self(sql)
    
    def commit(self):
        self('COMMIT;')
    
        
    def df(self, sql):
        # executes a sql statement and returns result in a dataframe
        # we need to use a cursor to obtain column names
        cur = self.conn.cursor().execute(sql)
        col_name_list = [tuple[0] for tuple in cur.description]
        res = pd.DataFrame(cur.fetchall(), columns=col_name_list)      
        cur.close()
        return res
    
    def tables(self):
        tables = self("SELECT name FROM sqlite_master WHERE type='table';")
        return [tab[0] for tab in tables]
    
    def count(self, table_name=None):
        if table_name:
            return (table_name, self(f"SELECT COUNT(*) FROM {table_name};")[0][0])
        else:
            return [self.count(table_name) for table_name in self.tables()]
        
    def count_distinct(self, table_name=None):
        if table_name:
            return (table_name, self(f"SELECT COUNT(*) FROM (SELECT DISTINCT * FROM {table_name});")[0][0])
        else:
            return [self.count(table_name) for table_name in self.tables()]
        
    
    def describe(self, table_name=None):
        # prints tables length and displays first 5 in a dataframe
        if table_name:
            print(self.count(table_name))
            return self.df(f"SELECT * FROM {table_name} LIMIT 5")
        else:
            tables = self.tables()
            dfs = [self.describe(table_name) for table_name in tables]
            htmls = []
            for i in range(len(dfs)):
                styler = dfs[i].T.style.set_table_attributes("style='display:inline'").set_caption(tables[i])
                htmls.append(styler._repr_html_())
            display_html(reduce(operator.add, htmls), raw=True)
            
    def insert(self, table, records):
        # simple insert, make sure the records are in the same order as the db fields!
        sql = f"INSERT INTO {table} VALUES ({','.join(['?']*len(records[0]))})"
        print(sql)
        for review in records:
            self.conn.execute(sql,review)
        self.conn.commit()
        return self.count(table)
    
    def __exit__(self):
        self.conn.close()
