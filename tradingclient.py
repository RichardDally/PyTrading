import time
import logging
import socket
import traceback
import errno
from feederhandler import FeederHandler
from orderhandler import OrderHandler


class TradingClient:
    def __init__(self, marshaller, login, password, host, feeder_port, matching_engine_port, uptime_in_seconds):
        self.logger = logging.getLogger(__name__)
        self.feedhandler = FeederHandler(marshaller=marshaller, host=host, port=feeder_port)
        self.orderhandler = OrderHandler(login=login, password=password, marshaller=marshaller, host=host, port=matching_engine_port)
        self.start_time = None
        self.stop_time = None
        if uptime_in_seconds:
            self.start_time = time.time()
            self.stop_time = self.start_time + uptime_in_seconds

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
        except KeyboardInterrupt:
            self.logger.info('Stopped by user')
        except socket.error as exception:
            # TODO: improve unable to connect exceptions like
            if exception.errno not in (errno.ECONNRESET, errno.ENOTCONN, errno.ECONNREFUSED):
                self.logger.warning('Client connection lost, unhandled errno [{}]'.format(exception.errno))
                self.logger.warning(traceback.print_exc())
        finally:
            for handler in handlers:
                handler.cleanup()
        self.logger.info('Client ends')


if __name__ == '__main__':
    import sys
    logging.basicConfig(stream=sys.stdout,
                        #filename=datetime.datetime.now().strftime("TradingClient_%Y%m%d_%H%M%S.log"),
                        level=logging.INFO,
                        format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S %p')
    try:
        from protobufserialization import ProtobufSerialization
    except ImportError as error:
        ProtobufSerialization = None
        print('Unable to start trading client. Reason [{}]'.format(error))
    else:
        client = TradingClient(login='RichardDally',
                               password='Password',
                               marshaller=ProtobufSerialization(),
                               host=socket.gethostbyname(socket.gethostname()),
                               feeder_port=50000,
                               matching_engine_port=50001,
                               uptime_in_seconds=None)
        client.start([client.feedhandler, client.orderhandler])
