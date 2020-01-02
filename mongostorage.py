from loguru import logger
from pymongo import MongoClient
from abstractstorage import AbstractStorage


class MongoStorage(AbstractStorage):
    def __init__(self, host, port):
        """
        Mind aggressive timeout on distant locations (3 seconds)
        """
        self.client = MongoClient(host=host, port=port, serverSelectionTimeoutMS=3000)
        self.client.admin.command("ismaster")
        self.database_name = "PyTrading"
        self.database = self.client[self.database_name]
        self.users_collection_name = "Users"
        self.orders_collection_name = "Orders"
        self.deals_collection_name = "Deals"
        self.users_collection = self.database[self.users_collection_name]
        self.orders_collection = self.database[self.orders_collection_name]
        self.deals_collection = self.database[self.deals_collection_name]

    def insert_user(self, login, password) -> None:
        user = {"login": login, "password": password}
        self.users_collection.insert_one(user)

    def is_valid_user(self, login, password) -> bool:
        document = {"login": login, "password": password}
        return self.users_collection.count(document) == 1

    def insert_order(self, order) -> None:
        self.orders_collection.insert_one(
            {
                "identifier": order.identifier,
                "way": order.way.way,
                "instrument_identifier": order.instrument_identifier,
                "quantity": order.quantity,
                "canceled_quantity": order.canceled_quantity,
                "executed_quantity": order.executed_quantity,
                "price": order.price,
                "counterparty": order.counterparty,
                "timestamp": order.timestamp,
            }
        )

    def delete_all_orders(self) -> None:
        delete_results = self.orders_collection.delete_many({})
        logger.info(f"Deleted orders [{delete_results.deleted_count}]")

    def insert_deal(self, deal) -> None:
        raise NotImplementedError()
