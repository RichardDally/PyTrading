from tcpserver import TcpServer
from tcpserver import ClosedConnection
from staticdata import StaticData


class Feeder(TcpServer):
    def __init__(self, marshaller, port):
        TcpServer.__init__(self, port)
        self.marshaller = marshaller
        self.referential = None
        self.initialize_referential()

    def get_referential(self):
        return self.referential

    def initialize_referential(self):
        self.logger.debug('Loading referential')
        self.referential = StaticData.get_default_referential()
        self.logger.debug('Referential is loaded')

    def on_accept_connection(self, **kwargs):
        sock = kwargs['sock']
        self.output_message_stacks[sock] = [self.marshaller.encode_referential(self.referential)]
        print('Feeder got connection from [{}]'.format(sock.getpeername()))

    def handle_readable_client(self, **kwargs):
        raise NotImplementedError('handle_readable_client')

    def send_one_peer_order_books(self, **kwargs):
        sock = kwargs.get('sock')
        self.logger.debug('Adding message to [{}]  message queue'.format(sock.getpeername()))
        for encoded_order_book in kwargs['encoded_order_books']:
            self.output_message_stacks[sock].append(encoded_order_book)
        self.logger.debug('Message queue size [{}] for [{}]'.format(len(self.output_message_stacks[sock]), sock.getpeername()))

    def send_all_order_books(self, order_books):
        encoded_order_books = []
        for _, order_book in order_books.items():
            encoded_order_books.append(self.marshaller.encode_order_book(order_book))
        for sock in self.inputs:
            if sock is self.listener:
                continue
            self.generic_handle(handler=self.send_one_peer_order_books, sock=sock, encoded_order_books=encoded_order_books)

        #print('SELF INPUTS {}'.format(len(self.inputs)))
        #print('ORDER BOOKS {}'.format(len(order_books)))
        #print('ENCODED ORDER BOOKS {}'.format(len(encoded_order_books)))
