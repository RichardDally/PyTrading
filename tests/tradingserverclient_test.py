import time
import socket
import unittest
from loguru import logger
from multiprocessing.pool import ThreadPool
from pytrading import random_string
from pytrading import SqliteStorage
from pytrading import OrderWay, Buy, Sell
from pytrading import TradingServer
from pytrading import TradingClient
from pytrading import ProtobufSerialization


class LiquidityTaker(TradingClient):
    """ LiquidityTaker is looking for all available orders and sends opposite way orders to clear order book"""

    def main_loop_hook(self):
        # Read the order books
        for _, order_book in self.feedhandler.order_books.items():
            all_orders = order_book.get_all_orders()

            # Create opposite orders to get executed on every order
            for order in all_orders:
                if order.counterparty != self.ordersender.login:
                    self.ordersender.push_order(way=OrderWay.get_opposite_way(order.way),
                                                price=order.price,
                                                quantity=order.quantity,
                                                instrument_identifier=order.instrument_identifier)


class LiquidityProvider(TradingClient):
    """ LiquidityProvider constantly sends orders to get executed """

    def __init__(self, *args, **kwargs):
        super(LiquidityProvider, self).__init__(*args, **kwargs)

    def main_loop_hook(self):
        # Get all instruments available
        instruments = self.feedhandler.referential.get_instruments()

        # Send buy and sell orders on each one (if not empty)
        for instrument in instruments:
            if instrument.identifier not in self.feedhandler.order_books:
                continue
            order_book = self.feedhandler.order_books[instrument.identifier]
            if order_book.count_bids() == 0:
                self.ordersender.push_order(way=Buy(),
                                            price=40.0,
                                            quantity=10.0,
                                            instrument_identifier=instrument.identifier)
            if order_book.count_asks() == 0:
                self.ordersender.push_order(way=Sell(),
                                            price=42.0,
                                            quantity=10.0,
                                            instrument_identifier=instrument.identifier)


class TestTradingServerClient(unittest.TestCase):
    """
    Start a server and two clients (one selling, the other buying)
    """

    @classmethod
    def setUpClass(cls):
        cls.liquidity_provider_login = random_string(length=4)
        cls.liquidity_taker_login = random_string(length=5)
        cls.client_password = random_string(length=6)
        cls.filename = ':memory:'

    def test_trading_server_and_client(self):
        thread_pool = ThreadPool(processes=3)
        async_server_result = thread_pool.apply_async(self.start_server)
        liquidity_provider_result = thread_pool.apply_async(self.start_liquidity_provider)
        liquidity_taker_result = thread_pool.apply_async(self.start_liquidity_taker)

        for failure in [async_server_result.get(), liquidity_taker_result.get(), liquidity_provider_result.get()]:
            if failure:
                self.fail(failure)

    def start_server(self):
        try:
            db = SqliteStorage(database_uri=self.filename)
            db.initialize()
            server = TradingServer(storage=db,
                                   client_authentication=False,
                                   marshaller=ProtobufSerialization(),
                                   feeder_port=60000,
                                   matching_engine_port=60001,
                                   uptime_in_seconds=3.0)

            server.start()
            db.close()
        except Exception as exception:
            logger.exception(exception)
            return exception
        return None

    def start_liquidity_taker(self):
        try:
            # Let the server starts properly...
            time.sleep(1)
            client = LiquidityTaker(login=self.liquidity_taker_login,
                                    password=self.client_password,
                                    marshaller=ProtobufSerialization(),
                                    host=socket.gethostbyname(socket.gethostname()),
                                    feeder_port=60000,
                                    matching_engine_port=60001,
                                    uptime_in_seconds=3.0)
            client.start([client.feedhandler, client.ordersender])
        except Exception as exception:
            logger.exception(exception)
            return exception
        return None

    def start_liquidity_provider(self):
        try:
            # Let the server starts properly...
            time.sleep(1)
            client = LiquidityProvider(login=self.liquidity_provider_login,
                                       password=self.client_password,
                                       marshaller=ProtobufSerialization(),
                                       host=socket.gethostbyname(socket.gethostname()),
                                       feeder_port=60000,
                                       matching_engine_port=60001,
                                       uptime_in_seconds=3.0)
            client.start([client.feedhandler, client.ordersender])
        except Exception as exception:
            logger.exception(exception)
            return exception
        return None
