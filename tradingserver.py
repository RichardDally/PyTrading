import time
import logging
import socket
import datetime
import traceback
from feeder import Feeder
from matchingengine import MatchingEngine


class TradingServer:
    def __init__(self, marshaller, feeder_port, matching_engine_port, uptime_in_seconds):
        self.feeder = Feeder(marshaller=marshaller, port=feeder_port)
        self.matching_engine = MatchingEngine(referential=self.feeder.get_referential(), marshaller=marshaller, port=matching_engine_port)
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
            print('Feeder listening on port [{}] for [{}] seconds'.format(self.feeder.port,
                                                                          self.stop_time - self.start_time))
            print('Matching engine listening on port [{}] for [{}] seconds'.format(self.matching_engine.port,
                                                                                   self.stop_time - self.start_time))
        else:
            print('Feeder listening on port [{}]'.format(self.feeder.port))
            print('Matching engine listening on port [{}]'.format(self.matching_engine.port))

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
            print('Stopped by user')
        except socket.error as exception:
            print('Trading server socket error [{}]'.format(exception))
            print(traceback.print_exc())
        finally:
            self.feeder.cleanup()
            self.matching_engine.cleanup()


if __name__ == '__main__':
    import sys
    logging.basicConfig(stream=sys.stdout,
                        #filename=datetime.datetime.now().strftime("TradingServer_%Y%m%d_%H%M%S.log"),
                        level=logging.INFO,
                        format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S %p')
    try:
        from protobufserialization import ProtobufSerialization
    except ImportError as error:
        ProtobufSerialization = None
        print('Unable to start trading server. Reason [{}]'.format(error))
    else:
        server = TradingServer(feeder_port=50000,
                               matching_engine_port=50001,
                               marshaller=ProtobufSerialization(),
                               uptime_in_seconds=None)
        server.start()
