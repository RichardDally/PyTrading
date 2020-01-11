import sqlite3
from abstractstorage import AbstractStorage


class SqliteStorage(AbstractStorage):
    def __init__(self, database_filename):
        self.database_filename = database_filename
        self.users_table = 'Users'
        self.connection = sqlite3.connect(self.database_filename)

    def initialize(self):
        c = self.connection.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS {} (login text unique, password text)'''.format(self.users_table))
        self.connection.commit()

    def close(self):
        self.connection.close()

    def insert_user(self, login, password) -> None:
        c = self.connection.cursor()
        query = "INSERT INTO {} (login, password) VALUES ('{}', '{}')".format(self.users_table, login, password)
        c.execute(query)
        self.connection.commit()

    def is_valid_user(self, login, password) -> bool:
        c = self.connection.cursor()
        t = (login,)
        c.execute('SELECT * FROM {} WHERE login=?'.format(self.users_table), t)
        stored_user = c.fetchone()
        if stored_user and login == stored_user[0] and password == stored_user[1]:
            return True
        return False
