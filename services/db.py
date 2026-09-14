import sqlite3

class Db:
    def __init__(self):
        self.connection = sqlite3.connect('sqlite.db')
        self.connection.row_factory = sqlite3.Row

    def query(self, sql, params={}, cls=''):
        cursor = self.connection.cursor()
        rows = cursor.execute(sql, params).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item_obj = cls()
            for title, value in item.items():
               title = '_' + title
               if hasattr(item_obj, title):
                   setattr(item_obj, title, value)
            items.append(item_obj) 
        return items