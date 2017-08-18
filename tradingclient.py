import logging
import socket
import select
from referential import Referential
from staticdata import MessageTypes


class TradingClient:
    def __init__(self, marshaller, feeder_port):
        self.marshaller = marshaller
        self.logger = logging.getLogger(__name__)
        self.feeder_port = feeder_port
        self.inputs = []
        self.buffer = bytearray()
        self.orderBooks = {}
        self.referential = Referential()
        self.handle_callbacks = {MessageTypes.Referential: self.handle_referential,
                                 MessageTypes.OrderBook: self.handle_order_book}

    def start(self):
        server_socket = None
        try:
            server_socket = socket.socket()
            server_socket.settimeout(10)
            host = socket.gethostname()

            print('Connecting on Feeder [{0}:{1}]'.format(host, self.feeder_port))
            server_socket.connect((host, self.feeder_port))

            self.inputs.append(server_socket)
            while self.inputs:
                readable, _, _ = select.select(self.inputs, [], [], 1)
                self.handle_readable(readable)
                decoded_messages_count, self.buffer = self.marshaller.decode_buffer(self.buffer, self.handle_callbacks)
                if decoded_messages_count == 0:
                    print('--- No decoded messages ---')
        except KeyboardInterrupt:
            print('Stopped by user')
        except socket.error:
            # TODO: client can be connected and raise this exception...
            print('Unable to connect to [{0}:{1}]'.format(host, self.feeder_port))
        finally:
            if server_socket:
                server_socket.close()
        print('Client ends')

    def handle_readable(self, readable):
        if len(readable) > 1:
            raise Exception('Readable must contain only 1 socket')

        for sock in readable:
            data = sock.recv(8192)
            if data:
                self.logger.debug('Adding server data ({}) to buffer'.format(len(data)))
                self.buffer += data
            else:
                print('Server closed its socket')
                self.inputs.remove(sock)

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
    except ImportError as error:
        print('Unable to start trading client. Reason [{}]'.format(error))
    else:
        client = TradingClient(marshaller=CapnpSerialization, feeder_port=50000)
        client.start()
