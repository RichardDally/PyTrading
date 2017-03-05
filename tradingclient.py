import logging
import socket
import struct
from instrument import Instrument
from referential import Referential
from serialization import Serialization

class TradingClient:
    logger = logging.getLogger(__name__)
    referential = Referential()
    orderBooks = {}
    buffer = None

    def __init__(self):
        pass

    """ public """
    def start(self):
        serverSocket = None

        try:
            serverSocket = socket.socket()
            host = socket.gethostname()
            port = 12345

            print('Connecting')
            serverSocket.connect((host, port))

            self.buffer = serverSocket.recv(4096)
            self.receive_referential(serverSocket)
            self.receive_order_book_full_snapshot(serverSocket)

        except KeyboardInterrupt:
            print('Stopped by user')
        except Exception, exception:
            print(exception)

        if serverSocket:
            serverSocket.close()

        print('Ok')

    """ private """
    def receive_referential(self, serverSocket):
        self.logger.debug('Receiving referential from [{}]'.format(serverSocket))

        messageLength = struct.unpack_from('>Q', self.buffer)[0]
        readableBytes = len(self.buffer) - 8
        if messageLength <= readableBytes:
            self.referential = Serialization.decode_referential(self.buffer[8 : 8 + messageLength])
            self.buffer = self.buffer[8 + messageLength:]
            print('Referential received:\n{}'.format(str(self.referential)))

    """ private """
    def receive_order_book_full_snapshot(self, serverSocket):
        self.logger.debug('Receiving order books full snapshot from [{}]'.format(serverSocket))

        messageLength = struct.unpack_from('>Q', self.buffer)[0]
        readableBytes = len(self.buffer) - 8
        if messageLength <= readableBytes:
            orderbook = Serialization.decode_orderbookfullsnapshot(self.buffer[8 : 8 + messageLength])
            self.buffer = self.buffer[8 + messageLength:]
            self.orderBooks[orderbook.instrument.id] = orderbook
            print('Order book received:{}'.format(str(orderbook)))

if __name__ == '__main__':
    logging.basicConfig(filename='TradingClient.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    client = TradingClient()
    client.start()
