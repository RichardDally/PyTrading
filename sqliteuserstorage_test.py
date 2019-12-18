import unittest
from sqliteuserstorage import SqliteUserStorage


class TestSqliteUserStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.login = 'rick'
        cls.password = 'rocks'
        cls.filename = ':memory:'
        cls.db = SqliteUserStorage(database_filename=cls.filename)

    def test_00_initialize(self):
        self.db.initialize()

    def test_01_insert_user(self):
        self.db.insert_user(login=self.login, password=self.password)

    def test_02_valid_user(self):
        self.db.is_valid_user(login=self.login, password=self.password)


if __name__ == '__main__':
    unittest.main()
