import logging
from tcpclient import TcpClient
from staticdata import MessageTypes


class FeederHandler(TcpClient):
    def __init__(self, marshaller, host, port):
        TcpClient.__init__(self, host, port)
        self.logger = logging.getLogger(__name__)
        self.marshaller = marshaller
        self.order_books = {}
        self.referential = None
        self.handle_callbacks = {MessageTypes.Referential.value: self.handle_referential,
                                 MessageTypes.OrderBook.value: self.handle_order_book}

    def handle_referential(self, new_referential):
        self.referential = new_referential
        self.logger.debug('Referential received:\n{}'.format(str(self.referential)))

    def handle_order_book(self, order_book):
        self.order_books[order_book.instrument_identifier] = order_book
        self.logger.debug('Order book [{}] updated:{}'.format(order_book.instrument_identifier, str(order_book)))

    def on_connect(self):
        pass

    def on_read_from_server(self):
        decoded_objects, self.received_buffer = self.marshaller.decode_buffer(self.received_buffer)
        for decoded_object in decoded_objects:
            self.handle_callbacks[decoded_object[0]](decoded_object[1])
        if len(decoded_objects) == 0:
            self.logger.info('--- No decoded messages ---')
