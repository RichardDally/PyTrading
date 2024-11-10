import sys
import time
import socket
from multiprocessing.pool import ThreadPool
from loguru import logger
from pymongo_inmemory import MongoClient
from pytrading import random_string
from pytrading import MongoStorage
from pytrading import Buy, Sell
from pytrading import TradingServer
from pytrading import TradingClient
from pytrading import ProtobufSerialization


class AbstractTrader(TradingClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_to_send = 1
        self.way = None

    def main_loop_hook(self):
        if self.order_to_send:
            self.ordersender.push_order(
                way=self.way,
                price=42.0,
                quantity=1.0,
                instrument_identifier=1
            )
            self.order_to_send -= 1


class BuyTrader(AbstractTrader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.way = Buy()


class SellTrader(AbstractTrader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.way = Sell()


class TradingSandbox:
    """
    Start a server and two clients (one selling, the other buying)
    """
    def __init__(self):
        self.serializer = ProtobufSerialization

    def start_all_components(self):
        thread_pool = ThreadPool(processes=3)
        async_server_result = thread_pool.apply_async(self.start_server)
        liquidity_provider_result = thread_pool.apply_async(self.start_selling)
        liquidity_taker_result = thread_pool.apply_async(self.start_buying)

        async_server_result.get()
        liquidity_taker_result.get()
        liquidity_provider_result.get()

    def start_server(self):
        """
        Using in-memory MongoDB client
        """
        try:
            db = MongoStorage(client=MongoClient())
            server = TradingServer(
                storage=db,
                client_authentication=False,
                marshaller=self.serializer(),
                feeder_port=60000,
                matching_engine_port=60001,
                uptime_in_seconds=3
            )
            server.start()
        except Exception as exception:
            logger.exception(exception)

    def start_selling(self):
        try:
            # Let the server starts properly...
            time.sleep(1)
            client = BuyTrader(login="HedgeFund",
                               password=random_string(length=5),
                               marshaller=self.serializer(),
                               host=socket.gethostbyname(socket.gethostname()),
                               feeder_port=60000,
                               matching_engine_port=60001,
                               uptime_in_seconds=3.0)
            client.start([client.feedhandler, client.ordersender])
        except Exception as exception:
            logger.exception(exception)
            return exception
        return None

    def start_buying(self):
        try:
            # Let the server starts properly...
            time.sleep(1)
            client = SellTrader(login="Bank",
                                password=random_string(length=5),
                                marshaller=self.serializer(),
                                host=socket.gethostbyname(socket.gethostname()),
                                feeder_port=60000,
                                matching_engine_port=60001,
                                uptime_in_seconds=3.0)
            client.start([client.feedhandler, client.ordersender])
        except Exception as exception:
            logger.exception(exception)


if __name__ == '__main__':
    logger.remove()
    logger.add(
        sink=sys.stdout,
        format="{time:HH:mm:ss} | {thread} | {level} | {message}",
        level="DEBUG",
        colorize=True,
    )
    sandbox = TradingSandbox()
    sandbox.start_all_components()
