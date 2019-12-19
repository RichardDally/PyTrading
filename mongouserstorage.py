from pymongo import MongoClient
from abstractstorage import AbstractStorage


class MongoStorage(AbstractStorage):
    def __init__(self, host, port):
        self.database_name = "PyTrading"
        self.client = MongoClient(host, port)
        self.database = self.client[self.database_name]
        self.users_collection_name = "Users"
        self.trades_collection_name = "Deals"
        self.user_collection = self.database[self.users_collection_name]
        self.deals_collection = self.database[self.trades_collection_name]

    def insert_user(self, login, password) -> None:
        user = {"login": login, "password": password}
        self.user_collection.insert_one(user)

    def is_valid_user(self, login, password) -> bool:
        document = {"login": login, "password": password}
        return self.user_collection.count(document) == 1

    def book_deal(self, deal) -> None:
        pass
