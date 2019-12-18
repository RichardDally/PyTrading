from pymongo import MongoClient
from abstractuserstorage import AbstractUserStorage
from loguru import logger


class MongoUserStorage(AbstractUserStorage):
    def __init__(self, host, port):
        self.database_name = "PyTrading"
        self.collection_name = "Users"
        logger.info('Connecting to database [{}]'.format(self.database_name))
        self.client = MongoClient(host, port)
        self.database = self.client[self.database_name]
        self.collection = self.database[self.collection_name]

    def insert_user(self, login, password):
        user = {"login": login, "password": password}
        self.collection.insert_one(user)

    def is_valid_user(self, login, password) -> bool:
        document = {"login": login, "password": password}
        return self.collection.count(document) == 1
