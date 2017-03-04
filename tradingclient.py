import logging
import socket
import capnp
import struct
import referential_capnp
from instrument import Instrument
from referential import Referential

class TradingClient:
    logger = logging.getLogger(__name__)
    referential = None
    orderBooks = None

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
            # TODO: fix receiving, send ACK to referential to get full snapshot
            self.receive_referential(serverSocket)
            #self.receive_order_books_full_snapshot(serverSocket)

        except KeyboardInterrupt:
            print('Stopped by user')
        except Exception, exception:
        # TODO: catch other exceptions
            print(exception)

        if serverSocket:
            serverSocket.close()

        print('Ok')

    """ private """
    def receive_referential(self, serverSocket):
        self.logger.debug('Receiving referential from [{}]'.format(serverSocket))
        buffer = serverSocket.recv(4096)

        messageLength = struct.unpack_from('>Q', buffer)[0]
        print(messageLength)

        readableBytes = len(buffer) - 8
        if messageLength <= readableBytes:
            self.referential = referential_capnp.Referential.from_bytes(buffer[8:8 + messageLength])
            print('Referential', self.referential)

    """ private """
    def receive_order_books_full_snapshot(self, serverSocket):
        self.logger.debug('Receiving order books full snapshot from [{}]'.format(serverSocket))
        buffer = serverSocket.recv(4096)
        self.orderBooks = pickle.loads(buffer)
        print('Order books', self.orderBooks)

if __name__ == '__main__':
    logging.basicConfig(filename='TradingClient.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    client = TradingClient()
    client.start()
