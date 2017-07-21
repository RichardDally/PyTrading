import sys
import unittest
import logging
import traceback
import time
from multiprocessing.pool import ThreadPool
from tradingserver import TradingServer
from tradingclient import TradingClient
from serialization_mock import SerializationMock


def start_server():
    try:
        server = TradingServer(s=SerializationMock, uptime_in_seconds=3.0)
        server.start()
    except Exception as exception:
        print(traceback.print_exc())
        return exception
    return None


def start_client():
    try:
        time.sleep(1)
        client = TradingClient(SerializationMock)
        client.start()
    except Exception as exception:
        print(traceback.print_exc())
        return exception
    return None


class TestTradingServerClient(unittest.TestCase):
    def test_trading_server_and_client(self):
        # TODO: fix logging to stdout
        logging.basicConfig(stream=sys.stdout,
                            level=logging.INFO,
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            datefmt='%d/%m/%Y %I:%M:%S %p')

        thread_pool = ThreadPool(processes=2)
        async_server_result = thread_pool.apply_async(start_server)
        async_client_reset = thread_pool.apply_async(start_client)

        server_failed = async_server_result.get()
        client_failed = async_client_reset.get()

        if server_failed:
            self.fail(server_failed)

        if client_failed:
            self.fail(client_failed)

if __name__ == '__main__':
    unittest.main()
