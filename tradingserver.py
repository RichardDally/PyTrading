import time
import socket
import traceback
from loguru import logger
from feeder import Feeder
from mongouserstorage import MongoUserStorage
from matchingengine import MatchingEngine


class TradingServer:
    """
    TradingServer holds two socket servers: a feeder and a matching engine.
    Feeder will stream referential (instruments that can be traded) and order books (orders placed by traders)
    Matching engine will handle orders received and send match confirmations (deal).
    SqliteUserStorage will contain traders credentials for authentication
    """
    def __init__(self, storage, marshaller, feeder_port, matching_engine_port, uptime_in_seconds):
        self.storage = storage
        self.feeder = Feeder(marshaller=marshaller, port=feeder_port)
        self.matching_engine = MatchingEngine(storage=self.storage,
                                              referential=self.feeder.get_referential(),
                                              marshaller=marshaller,
                                              port=matching_engine_port)
        self.start_time = None
        self.stop_time = None
        if uptime_in_seconds:
            self.start_time = time.time()
            self.stop_time = self.start_time + uptime_in_seconds

    def reached_uptime(self):
        if self.stop_time:
            return time.time() >= self.stop_time
        return False

    def print_listen_messages(self):
        if self.start_time and self.stop_time:
            duration = self.stop_time - self.start_time
            logger.info('Feeder listening on port [{}] for [{}] seconds'.format(self.feeder.port, duration))
            logger.info('Matching engine listening on port [{}] for [{}] seconds'.format(self.matching_engine.port, duration))
        else:
            logger.info('Feeder listening on port [{}]'.format(self.feeder.port))
            logger.info('Matching engine listening on port [{}]'.format(self.matching_engine.port))

    def start(self):
        try:
            self.feeder.listen()
            self.matching_engine.listen()
            self.print_listen_messages()
            while not self.reached_uptime():
                self.matching_engine.process_sockets()
                self.feeder.process_sockets()
                self.feeder.send_all_order_books(self.matching_engine.get_order_books())
        except KeyboardInterrupt:
            logger.info('Stopped by user')
        except socket.error as exception:
            logger.error('Trading server socket error [{}]'.format(exception))
            logger.error(traceback.print_exc())
        finally:
            self.feeder.cleanup()
            self.matching_engine.cleanup()


if __name__ == '__main__':
    try:
        from protobufserialization import ProtobufSerialization
        login = 'rick'
        password = 'pass'
        db = MongoUserStorage(host="localhost", port=27017)
        db.initialize()
        if not db.is_valid_user(login=login, password=password):
            db.insert_user(login=login, password=password)
        server = TradingServer(storage=db,
                               feeder_port=50000,
                               matching_engine_port=50001,
                               marshaller=ProtobufSerialization(),
                               uptime_in_seconds=None)
        server.start()
        db.close()
    except ImportError as error:
        ProtobufSerialization = None
        logger.critical('Unable to start trading server. Reason [{}]'.format(error))
