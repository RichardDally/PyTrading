import logging
import traceback
from order import Order
from orderbook import OrderBook
from tcpserver import TcpServer
from staticdata import MessageTypes
from sessionstatus import SessionStatus


# TODO: move elsewhere exceptions
class LogonRejected(BaseException):
    """ Client logon attempt is rejected """
    def __init__(self, reason):
        self.reason = reason


class OrderRejected(BaseException):
    """ Order creation is rejected """
    def __init__(self, reason):
        self.reason = reason


class MatchingEngine(TcpServer):
    def __init__(self, storage, referential, marshaller, port):
        TcpServer.__init__(self, port)
        self.logger = logging.getLogger(__name__)
        self.storage = storage
        self.marshaller = marshaller
        self.referential = referential
        self.order_books = {}
        self.initialize_order_books()
        self.handle_callbacks = {MessageTypes.Logon.value: self.handle_logon,
                                 MessageTypes.CreateOrder.value: self.handle_create_order}

    def on_accept_connection(self, **kwargs):
        client_session = kwargs['client_session']
        self.logger.info('Matching engine got connection from [{}]'.format(client_session.peer_name))

    def handle_logon(self, logon, sock):
        client_session = self.client_sessions[sock]
        client_session.login = logon.login

        for cs in self.client_sessions.values():
            if logon.login == cs.login and cs.status == SessionStatus.Authenticated:
                raise LogonRejected(reason='Already connected')

        if not self.storage.is_valid_user(login=logon.login, password=logon.password):
            raise LogonRejected(reason='Unknown user')

        client_session.password = logon.password
        client_session.status = SessionStatus.Authenticated
        self.logger.info('[{}] is now [{}]'.format(logon.login, client_session.status.name))

    def handle_create_order(self, create_order, sock):
        client_session = self.client_sessions[sock]
        if client_session.status != SessionStatus.Authenticated:
            raise OrderRejected('Client is not authenticated')

        # TODO: does client session is allowed to create orders ?

        try:
            self.logger.info('Create order for {}'.format(client_session))
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
        client_session = self.client_sessions[kwargs['sock']]
        decoded_objects, client_session.received_buffer = self.marshaller.decode_buffer(client_session.received_buffer)
        for decoded_object in decoded_objects:
            try:
                self.handle_callbacks[decoded_object[0]](decoded_object[1], client_session.sock)
            except Exception as exception:
                self.logger.error('Matching engine, handle_readable_client failed [{}]'.format(exception))
                self.logger.error(traceback.print_exc())
            except LogonRejected as exception:
                self.logger.info('[{}] logon attempt from [{}] is rejected. Reason [{}]'
                                 .format(client_session.login, client_session.peer_name, exception.reason))
                self.remove_client_socket(client_session.sock)
                break
            except OrderRejected as exception:
                self.logger.error('[{}] order attempt from [{}] is rejected. Reason [{}]'
                                  .format(client_session.login, client_session.peer_name, exception.reason))
                self.remove_client_socket(client_session.sock)
                break
        if len(decoded_objects) == 0:
            self.logger.info('--- No decoded messages ---')
