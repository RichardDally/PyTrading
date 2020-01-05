import unittest
from toolbox import random_string
from sqliteuserstorage import SqliteStorage


class TestSqliteUserStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.login = random_string(length=5)
        cls.password = random_string(length=5)
        cls.filename = ':memory:'
        cls.db = SqliteStorage(database_filename=cls.filename)

    def test_00_initialize(self):
        self.db.initialize()

    def test_01_insert_user(self):
        self.db.insert_user(login=self.login, password=self.password)

    def test_02_valid_user(self):
        self.db.is_valid_user(login=self.login, password=self.password)
