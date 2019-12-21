import time
import socket
import traceback
import errno
from feederhandler import FeederHandler
from ordersender import OrderSender
from abc import ABCMeta, abstractmethod
from exceptions import ClosedConnection
from orderway import Buy, Sell
from loguru import logger


class TradingClient:
    """
    TradingClient holds two client sockets: a feeder handler and an order sender.
    Feeder handler will receive referential (instruments that can be traded) and orders from the feeder.
    Order sender will send orders and receive deal confirmations.
    """
    __metaclass__ = ABCMeta

    def __init__(self, marshaller, login, password, host, feeder_port, matching_engine_port, uptime_in_seconds):
        self.feedhandler = FeederHandler(marshaller=marshaller, host=host, port=feeder_port)
        self.ordersender = OrderSender(login=login, password=password, marshaller=marshaller,
                                       host=host, port=matching_engine_port)
        self.start_time = None
        self.stop_time = None
        if uptime_in_seconds:
            self.start_time = time.time()
            self.stop_time = self.start_time + uptime_in_seconds

    @abstractmethod
    def main_loop_hook(self):
        """ Your trading algorithm goes here :) """
        pass

    def reached_uptime(self):
        if self.stop_time:
            return time.time() >= self.stop_time
        return False

    @staticmethod
    def all_connected(handlers):
        for handler in handlers:
            if not handler.is_connected():
                return False
        return True

    def start(self, handlers):
        try:
            for handler in handlers:
                handler.connect()
            while not self.reached_uptime() and self.all_connected(handlers):
                for handler in handlers:
                    handler.process_sockets()
                self.main_loop_hook()
        except ClosedConnection:
            pass
        except KeyboardInterrupt:
            logger.info('Stopped by user')
        except socket.error as exception:
            # TODO: improve unable to connect exceptions like
            if exception.errno not in (errno.ECONNRESET, errno.ENOTCONN, errno.ECONNREFUSED):
                logger.warning('Client connection lost, unhandled errno [{}]'.format(exception.errno))
                logger.warning(traceback.print_exc())
        finally:
            for handler in handlers:
                handler.cleanup()
        logger.info('[{}] ends'.format(self.__class__.__name__))


class BasicClient(TradingClient):
    def __init__(self, *args, **kwargs):
        super(BasicClient, self).__init__(*args, **kwargs)
        self.send_one_order = True

    def main_loop_hook(self):
        if self.send_one_order:
            first_instrument = self.feedhandler.referential.get_instruments()[0]
            self.ordersender.push_order(way=Buy(),
                                        price=42.0,
                                        quantity=10.0,
                                        instrument_identifier=first_instrument.identifier)
            self.ordersender.push_order(way=Sell(),
                                        price=42.0,
                                        quantity=10.0,
                                        instrument_identifier=first_instrument.identifier)
            self.send_one_order = False
            logger.debug("ORDER SENT")


if __name__ == '__main__':
    try:
        from protobufserialization import ProtobufSerialization
        client = BasicClient(login="rick",
                             password="pass",
                             marshaller=ProtobufSerialization(),
                             host=socket.gethostbyname(socket.gethostname()),
                             feeder_port=50000,
                             matching_engine_port=50001,
                             uptime_in_seconds=None)
        client.start([client.feedhandler, client.ordersender])
    except ImportError as error:
        ProtobufSerialization = None
        logger.critical(f"Unable to start trading client. Reason [{error}]")
