import logging
import socket
import struct
import select
from instrument import Instrument
from referential import Referential
from serialization import Serialization

class TradingClient:
    def __init__(self):
        self.inputs = []
        self.buffer = ''
        self.orderBooks = {}
        self.decode_buffer = None
        self.logger = logging.getLogger(__name__)
        self.referential = Referential()

    """ public """
    def start(self):
        serverSocket = None

        try:
            serverSocket = socket.socket()
            host = socket.gethostname()
            port = 12345

            print('Connecting')
            serverSocket.connect((host, port))

            self.inputs.append(serverSocket)
            self.decode_buffer = self.decode_referential
            while self.inputs:
                print('---')
                readable, writable, exceptional = select.select(self.inputs, [], [], 1)
                self.handle_readable(readable)
                while len(self.buffer) > 8:
                    self.decode_buffer()

        except KeyboardInterrupt:
            print('Stopped by user')
        except Exception, exception:
            print(exception)

        if serverSocket:
            serverSocket.close()

        print('Ok')

    def handle_readable(self, readable):
        assert(len(readable) <= 1), 'Readable must contain only 1 socket'
        for s in readable:
            data = s.recv(4096)
            if data:
                self.buffer += data
            else:
                print('Server closed its socket')
                self.inputs.remove(s)

    """ private """
    def decode_referential(self):
        messageLength = struct.unpack_from('>Q', self.buffer)[0]
        readableBytes = len(self.buffer) - 8
        if messageLength <= readableBytes:
            self.referential = Serialization.decode_referential(self.buffer[8 : 8 + messageLength])
            print('Buffer length before [{}]'.format(len(self.buffer)))
            self.buffer = self.buffer[8 + messageLength:]
            print('Buffer length after [{}]'.format(len(self.buffer)))
            print('Referential received:\n{}'.format(str(self.referential)))
            self.decode_buffer = self.decode_orderbookfullsnapshot

    """ private """
    def decode_orderbookfullsnapshot(self):
        messageLength = struct.unpack_from('>Q', self.buffer)[0]
        readableBytes = len(self.buffer) - 8
        if messageLength <= readableBytes:
            orderbook = Serialization.decode_orderbookfullsnapshot(self.buffer[8 : 8 + messageLength])
            print('Buffer length before [{}]'.format(len(self.buffer)))
            self.buffer = self.buffer[8 + messageLength:]
            print('Buffer length after [{}]'.format(len(self.buffer)))
            self.orderBooks[orderbook.instrument.id] = orderbook
            print('Order book received:{}'.format(str(orderbook)))

if __name__ == '__main__':
    logging.basicConfig(filename='TradingClient.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    client = TradingClient()
    client.start()
