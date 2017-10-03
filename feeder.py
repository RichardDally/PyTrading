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

    def on_accept_connection(self, sock):
        self.message_stacks[sock] = [self.marshaller.encode_referential(self.referential)]
        print('Feeder got connection from [{}]'.format(sock.getpeername()))

    def handle_readable_client(self, sock):
        data = sock.recv(8192)
        if not data:
            raise ClosedConnection

    def send_order_books(self, order_books):
        encoded_order_books = []
        for _, order_book in order_books.items():
            encoded_order_books.append(self.marshaller.encode_order_book(order_book))
        for sock in self.inputs:
            if sock is self.listener:
                continue
            self.logger.debug('Adding message to [{}]  message queue'.format(sock.getpeername()))
            for encoded_order_book in encoded_order_books:
                self.message_stacks[sock].append(encoded_order_book)
            self.logger.debug('Message queue size [{}] for [{}]'.format(len(self.message_stacks[sock]), sock.getpeername()))

        #print('SELF INPUTS {}'.format(len(self.inputs)))
        #print('ORDER BOOKS {}'.format(len(order_books)))
        #print('ENCODED ORDER BOOKS {}'.format(len(encoded_order_books)))
