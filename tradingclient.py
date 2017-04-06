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
        self.logger = logging.getLogger(__name__)
        self.referential = Referential()
        self.decodeMapping = { 'R' : self.handle_referential, 'S' : self.handle_orderbookfullsnapshot }


    """ public """
    def start(self):
        serverSocket = None

        try:
            serverSocket = socket.socket()
            host = socket.gethostname()
            port = 12345

            print('Connecting on [{0}:{1}]'.format(host, port))
            serverSocket.connect((host, port))

            self.inputs.append(serverSocket)
            while self.inputs:
                readable, writable, exceptional = select.select(self.inputs, [], [], 1)
                self.handle_readable(readable)
                while len(self.buffer) > 9:
                    print('Decoding buffer remaining size [{}]'.format(len(self.buffer)))
                    if not self.decode_buffer():
                        break
                print('---')
        except KeyboardInterrupt:
            print('Stopped by user')
        except Exception, exception:
            print(exception)

        if serverSocket:
            serverSocket.close()

        print('Ok')


    """ private """
    def handle_readable(self, readable):
        assert(len(readable) <= 1), 'Readable must contain only 1 socket'
        for s in readable:
            data = s.recv(4096)
            if data:
                print('Adding server data ({}) to buffer'.format(len(data)))
                self.buffer += data
            else:
                print('Server closed its socket')
                self.inputs.remove(s)


    """ private """
    def handle_referential(self, buffer):
        self.referential = Serialization.decode_referential(buffer)
        print('Referential received:\n{}'.format(str(self.referential)))


    """ private """
    def handle_orderbookfullsnapshot(self, buffer):
        orderbook = Serialization.decode_orderbookfullsnapshot(buffer)
        print('Order book received:{}'.format(str(orderbook)))


    """ private """
    def decode_buffer(self):
        # TODO: handle empty messageType case
        messageLength, messageType = struct.unpack_from('>Qc', self.buffer)
        headerSize = 9
        readableBytes = len(self.buffer) - headerSize
        print('Message length [{}]'.format(messageLength))
        print('Message type [{}]'.format(messageType))
        if messageLength <= readableBytes:
            self.decodeMapping[messageType](self.buffer[headerSize : headerSize + messageLength])
            print('Buffer length before [{}]'.format(len(self.buffer)))
            self.buffer = self.buffer[headerSize + messageLength:]
            print('Buffer length after [{}]'.format(len(self.buffer)))
            return True
        return False

if __name__ == '__main__':
    logging.basicConfig(filename='TradingClient.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    client = TradingClient()
    client.start()
