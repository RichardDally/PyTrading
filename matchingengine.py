from orderbook import OrderBook
from tcpserver import TcpServer
from tcpserver import ClosedConnection


class MatchingEngine(TcpServer):
    def __init__(self, referential, marshaller, port):
        TcpServer.__init__(self, port)
        self.marshaller = marshaller
        self.referential = referential
        self.order_books = {}
        self.initialize_order_books()

    def get_order_books(self):
        return self.order_books

    def initialize_order_books(self):
        self.logger.debug('Initializing order books')
        # TODO: use generator
        for instrument in self.referential.instruments:
            self.order_books[instrument.identifier] = OrderBook(instrument.identifier)
        self.logger.debug('[{}] order books are initialized'.format(len(self.referential)))

    def on_accept_connection(self, sock):
        self.message_stacks[sock] = []
        print('Matching engine got connection from [{}]'.format(sock.getpeername()))

    def handle_readable_client(self, sock):
        data = sock.recv(8192)
        if not data:
            raise ClosedConnection
