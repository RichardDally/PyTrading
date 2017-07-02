import logging
import socket
import struct
import select
from referential import Referential


class TradingClient:
    def __init__(self, s):
        self.s = s
        self.logger = logging.getLogger(__name__)
        self.port = 12345
        self.inputs = []
        self.buffer = ''
        self.orderBooks = {}
        self.referential = Referential()
        self.handle_callbacks = {'R': self.handle_referential,
                                 'O': self.handle_order_book}

    def start(self):
        server_socket = None
        try:
            server_socket = socket.socket()
            host = socket.gethostname()

            print('Connecting on [{0}:{1}]'.format(host, self.port))
            server_socket.connect((host, self.port))

            self.inputs.append(server_socket)
            while self.inputs:
                readable, _, exceptional = select.select(self.inputs, [], [], 1)
                self.handle_readable(readable)
                decoded_messages_count, self.buffer = self.s.decode_buffer(self.buffer, self.handle_callbacks)
                if decoded_messages_count == 0:
                    print('--- No decoded messages ---')
        except KeyboardInterrupt:
            print('Stopped by user')
        except socket.error:
            print('Unable to connect to [{0}:{1}]'.format(host, self.port))
        finally:
            if server_socket:
                server_socket.close()
        print('Client ends')

    def handle_readable(self, readable):
        assert(len(readable) <= 1), 'Readable must contain only 1 socket'
        for s in readable:
            data = s.recv(8192)
            if data:
                self.logger.debug('Adding server data ({}) to buffer'.format(len(data)))
                self.buffer += data.decode('utf-8')
            else:
                print('Server closed its socket')
                self.inputs.remove(s)

    def handle_referential(self, new_referential):
        self.referential = new_referential
        self.logger.debug('Referential received:\n{}'.format(str(self.referential)))

    def handle_order_book(self, order_book):
        self.logger.debug('Order book received:{}'.format(str(order_book)))


if __name__ == '__main__':
    logging.basicConfig(filename='TradingClient.log',
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    try:
        from capnpserialization import CapnpSerialization
        client = TradingClient(CapnpSerialization)
        client.start()
    except ImportError as error:
        print('Unable to start trading client. [{}]'.format(error))
