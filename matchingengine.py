import logging
import traceback
from order import Order
from orderbook import OrderBook
from tcpserver import TcpServer
from staticdata import MessageTypes
from sessionstatus import SessionStatus
from clientsession import ClientSession


class MatchingEngine(TcpServer):
    def __init__(self, referential, marshaller, port):
        TcpServer.__init__(self, port)
        self.logger = logging.getLogger(__name__)
        self.marshaller = marshaller
        self.referential = referential
        self.order_books = {}
        self.initialize_order_books()
        self.handle_callbacks = {MessageTypes.Logon: self.handle_logon,
                                 MessageTypes.CreateOrder: self.handle_create_order}

    def on_accept_connection(self, **kwargs):
        sock = kwargs['sock']
        self.output_message_stacks[sock] = []
        client_session = ClientSession(status=SessionStatus(SessionStatus.Handshaking),
                                       sock=sock, peer_name=sock.getpeername())
        self.client_sessions[sock] = client_session
        self.logger.info('Matching engine got connection from [{}]'.format(client_session.peer_name))

    def handle_logon(self, logon, sock):
        client_session = self.client_sessions[sock]
        # TODO: search login among authorized ones
        client_session.login = logon.login
        client_session.password = logon.password
        client_session.status = SessionStatus(SessionStatus.Authenticated)
        self.logger.info('Logon handled [{}], for [{}]'.format(logon, client_session.peer_name))

    def handle_create_order(self, create_order, sock):
        client_session = self.client_sessions[sock]
        # TODO: does client session is allowed to create orders ?
        # TODO: does client is authenticated ?
        try:
            order_book = self.order_books[create_order.instrument_identifier]
        except KeyError:
            self.logger.warning('Order book related to instrument identifier [{}] does not exist'
                                .format(create_order.instrument_identifier))
        else:
            new_order = Order(way=create_order.way,
                              instrument_identifier=create_order.instrument_identifier,
                              quantity=create_order.quantity,
                              price=create_order.price,
                              counterparty=client_session.login)
            order_book.on_new_order(new_order)

    def get_order_books(self):
        return self.order_books

    def initialize_order_books(self):
        self.logger.debug('Initializing order books')
        # TODO: use generator
        for instrument in self.referential.instruments:
            self.order_books[instrument.identifier] = OrderBook(instrument.identifier)
        self.logger.debug('[{}] order books are initialized'.format(len(self.referential)))

    def handle_readable_client(self, **kwargs):
        decoded_objects, self.received_buffer = self.marshaller.decode_buffer(self.received_buffer)
        for decoded_object in decoded_objects:
            try:
                self.handle_callbacks[decoded_object[0]](decoded_object[1], kwargs['sock'])
            except Exception as exception:
                self.logger.error('Matching engine, handle_readable_client failed [{}]'.format(exception))
                self.logger.error(traceback.print_exc())
        if len(decoded_objects) == 0:
            self.logger.info('--- No decoded messages ---')
