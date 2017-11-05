from tcpclient import TcpClient
from staticdata import MessageTypes


class FeederHandler(TcpClient):
    def __init__(self, marshaller, host, port):
        TcpClient.__init__(self, host, port)
        self.marshaller = marshaller
        self.referential = None
        self.handle_callbacks = {MessageTypes.Referential: self.handle_referential,
                                 MessageTypes.OrderBook: self.handle_order_book}

    def handle_referential(self, new_referential):
        self.referential = new_referential
        self.logger.debug('Referential received:\n{}'.format(str(self.referential)))

    def handle_order_book(self, order_book):
        self.logger.debug('Order book received:{}'.format(str(order_book)))

    def on_connect(self):
        pass

    def on_read_from_server(self):
        decoded_messages_count, self.server_buffer = self.marshaller.decode_buffer(self.server_buffer,
                                                                                   self.handle_callbacks)
        if decoded_messages_count == 0:
            print('--- No decoded messages ---')

    def on_write_to_server(self, sock):
        pass
