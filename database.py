import sys
import sqlite3
import logging
from storage import Storage


class Database(Storage):
    def __init__(self, database_filename):
        self.logger = logging.getLogger(__name__)
        self.database_filename = database_filename
        self.users_table = 'Users'
        self.connection = sqlite3.connect(self.database_filename)

    def initialize(self):
        c = self.connection.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS {} (login text unique, password text)'''.format(self.users_table))
        self.connection.commit()

    def close(self):
        self.connection.close()

    def insert_user(self, login, password):
        c = self.connection.cursor()
        query = "INSERT INTO {} (login, password) VALUES ('{}', '{}')".format(self.users_table, login, password)
        c.execute(query)
        self.connection.commit()

    def is_valid_user(self, login, password):
        c = self.connection.cursor()
        t = (login,)
        c.execute('SELECT * FROM {} WHERE login=?'.format(self.users_table), t)
        stored_user = c.fetchone()
        if stored_user and login == stored_user[0] and password == stored_user[1]:
            return True
        return False


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S %p')
