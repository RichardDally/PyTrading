from orderbook import OrderBook
from tcpserver import TcpServer
from staticdata import MessageTypes


class MatchingEngine(TcpServer):
    def __init__(self, referential, marshaller, port):
        TcpServer.__init__(self, port)
        self.marshaller = marshaller
        self.referential = referential
        self.order_books = {}
        self.initialize_order_books()
        self.handle_callbacks = {MessageTypes.CreateOrder: self.handle_create_order}

    def handle_create_order(self, create_order):
        print('HANDLE CREATE ORDER')
        print(create_order)
        # TODO: validate create order request and add it to order book

    def get_order_books(self):
        return self.order_books

    def initialize_order_books(self):
        self.logger.debug('Initializing order books')
        # TODO: use generator
        for instrument in self.referential.instruments:
            self.order_books[instrument.identifier] = OrderBook(instrument.identifier)
        self.logger.debug('[{}] order books are initialized'.format(len(self.referential)))

    def on_accept_connection(self, **kwargs):
        sock = kwargs['sock']
        self.output_message_stacks[sock] = []
        print('Matching engine got connection from [{}]'.format(sock.getpeername()))

    def handle_readable_client(self, **kwargs):
        decoded_messages_count, self.received_buffer = self.marshaller.decode_buffer(self.received_buffer,
                                                                                     self.handle_callbacks)
        if decoded_messages_count == 0:
            print('--- No decoded messages ---')
