import time
import logging
import socket
import traceback
import errno
from feederhandler import FeederHandler
from orderhandler import OrderHandler


class TradingClient:
    def __init__(self, marshaller, host, feeder_port, matching_engine_port, uptime_in_seconds):
        self.feedhandler = FeederHandler(marshaller=marshaller, host=host, port=feeder_port)
        self.orderhandler = OrderHandler(marshaller=marshaller, host=host, port=matching_engine_port)
        self.start_time = None
        self.stop_time = None
        if uptime_in_seconds:
            self.start_time = time.time()
            self.stop_time = self.start_time + uptime_in_seconds

    def reached_uptime(self):
        if self.stop_time:
            return time.time() >= self.stop_time
        return False

    def start(self):
        try:
            self.feedhandler.connect()
            self.orderhandler.connect()
            while not self.reached_uptime() and self.feedhandler.is_connected() and self.orderhandler.is_connected():
                self.feedhandler.process_sockets()
                self.orderhandler.process_sockets()
        except KeyboardInterrupt:
            print('Stopped by user')
        except socket.error as exception:
            if exception.errno not in (errno.ECONNRESET, errno.ENOTCONN, errno.ECONNREFUSED):
                print('Client connection lost, unhandled errno [{}]'.format(exception.errno))
                print(traceback.print_exc())
        finally:
            self.feedhandler.cleanup()
            self.orderhandler.cleanup()
        print('Client ends')


if __name__ == '__main__':
    logging.basicConfig(filename='TradingClient.log',
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    try:
        from protobufserialization import ProtobufSerialization
    except ImportError as error:
        ProtobufSerialization = None
        print('Unable to start trading client. Reason [{}]'.format(error))
    else:
        client = TradingClient(marshaller=ProtobufSerialization(),
                               host=socket.gethostbyname(socket.gethostname()),
                               feeder_port=50000,
                               matching_engine_port=50001,
                               uptime_in_seconds=None)
        client.start()
