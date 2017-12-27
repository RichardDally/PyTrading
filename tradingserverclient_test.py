import os
import sys
import time
import socket
import unittest
import logging
import traceback
from database import Database
from multiprocessing.pool import ThreadPool
from tradingserver import TradingServer
from tradingclient import TradingClient
from simpleserialization import SimpleSerialization


class TestTradingServerClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.login = 'rick'
        cls.password = 'pass'
        cls.filename = 'TradingServerClientTest.db'

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.filename)

    def test_trading_server_and_client(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.INFO,
                            format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                            datefmt='%d/%m/%Y %H:%M:%S')

        thread_pool = ThreadPool(processes=2)
        async_server_result = thread_pool.apply_async(self.start_server)
        async_client_reset = thread_pool.apply_async(self.start_client)

        server_failed = async_server_result.get()
        client_failed = async_client_reset.get()

        if server_failed:
            self.fail(server_failed)

        if client_failed:
            self.fail(client_failed)

    def start_server(self):
        try:
            db = Database(database_filename=self.filename)
            db.initialize()
            db.insert_user(login=self.login, password=self.password)
            server = TradingServer(storage=db,
                                   marshaller=SimpleSerialization(),
                                   feeder_port=60000,
                                   matching_engine_port=60001,
                                   uptime_in_seconds=3.0)

            server.start()
        except Exception as exception:
            print(traceback.print_exc())
            return exception
        return None

    def start_client(self):
        try:
            time.sleep(1)
            client = TradingClient(login=self.login,
                                   password=self.password,
                                   marshaller=SimpleSerialization(),
                                   host=socket.gethostbyname(socket.gethostname()),
                                   feeder_port=60000,
                                   matching_engine_port=60001,
                                   uptime_in_seconds=3.0)
            client.start([client.feedhandler, client.orderhandler])
        except Exception as exception:
            print(traceback.print_exc())
            return exception
        return None


if __name__ == '__main__':
    unittest.main()
