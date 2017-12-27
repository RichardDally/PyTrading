from tcpserver import TcpServer
from staticdata import StaticData
from sessionstatus import SessionStatus


class Feeder(TcpServer):
    def __init__(self, marshaller, port):
        TcpServer.__init__(self, port)
        self.marshaller = marshaller
        self.referential = None
        self.initialize_referential()

    def get_referential(self):
        return self.referential

    def initialize_referential(self):
        self.logger.info('Loading referential')
        self.referential = StaticData.get_default_referential()
        self.logger.info('Referential is loaded')

    def on_accept_connection(self, **kwargs):
        client_session = kwargs['client_session']
        # No authentication for Feed (for the moment)
        client_session.status = SessionStatus.Authenticated
        client_session.output_message_stack.append(self.marshaller.encode_referential(self.referential))
        self.logger.info('Feeder got connection from [{}]'.format(client_session.peer_name))

    def handle_readable_client(self, **kwargs):
        raise NotImplementedError('handle_readable_client')

    def send_one_peer_order_books(self, **kwargs):
        sock = kwargs['sock']
        client_session = self.client_sessions[sock]
        self.logger.debug('Adding message to [{}]  message queue'.format(client_session.peer_name))
        for encoded_order_book in kwargs['encoded_order_books']:
            client_session.output_message_stack.append(encoded_order_book)
        self.logger.debug('Message queue size [{}] for [{}]'.format(len(client_session.output_message_stack), client_session.peer_name))

    def send_all_order_books(self, order_books):
        encoded_order_books = []
        for _, order_book in order_books.items():
            encoded_order_books.append(self.marshaller.encode_order_book(order_book))
        for sock in self.inputs:
            if sock is self.listener:
                continue
            self.generic_handle(handler=self.send_one_peer_order_books, sock=sock, encoded_order_books=encoded_order_books)
