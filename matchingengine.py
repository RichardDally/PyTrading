from loguru import logger
from typing import Dict
from serverorder import ServerOrder
from orderbook import OrderBook
from tcpserver import TcpServer
from staticdata import MessageTypes
from sessionstatus import SessionStatus
from exceptions import LogonRejected, OrderRejected
from abstractstorage import AbstractStorage
from serialization import Serialization


class MatchingEngine(TcpServer):
    def __init__(self,
                 storage: AbstractStorage,
                 client_authentication: bool,
                 marshaller: Serialization,
                 port: int):
        TcpServer.__init__(self, port)
        self.storage = storage
        self.client_authentication = client_authentication
        self.marshaller = marshaller
        self.order_books = {}
        self.handle_callbacks = {MessageTypes.Logon.value: self.handle_logon,
                                 MessageTypes.CreateOrder.value: self.handle_create_order}
        logger.info(f"Client authentication has been [{'enabled' if self.client_authentication else 'disabled'}]")

    def cleanup(self):
        """
        Remove all orders if any storage used
        TODO: make this feature as an option
        """
        super().cleanup()
        if self.storage:
            logger.debug("Cleaning up orders")
            self.storage.delete_all_orders()

    def on_accept_connection(self, **kwargs):
        client_session = kwargs['client_session']
        logger.info(f"Matching engine got connection from [{client_session.peer_name}]")

    def handle_logon(self, logon, sock):
        client_session = self.client_sessions[sock]
        client_session.login = logon.login

        for cs in self.client_sessions.values():
            if logon.login == cs.login and cs.status == SessionStatus.Authenticated:
                raise LogonRejected(reason="Already connected")

        if self.client_authentication:
            if self.storage and not self.storage.is_valid_user(login=logon.login, password=logon.password):
                raise LogonRejected(reason="Unknown user")

        client_session.password = logon.password
        client_session.status = SessionStatus.Authenticated
        if self.client_authentication:
            logger.info(f"[{logon.login}] is now [{client_session.status.name}]")
        else:
            logger.info(f"[{logon.login}] has been automatically [{client_session.status.name}]")

    def handle_create_order(self, create_order, sock):
        client_session = self.client_sessions[sock]
        if client_session.status != SessionStatus.Authenticated:
            raise OrderRejected("Client is not authenticated")

        # TODO: does client session is allowed to create orders ?

        try:
            logger.info('Create order for {}'.format(client_session))
            order_book = self.order_books[create_order.instrument_identifier]
            new_order = ServerOrder(way=create_order.way,
                                    instrument_identifier=create_order.instrument_identifier,
                                    quantity=create_order.quantity,
                                    price=create_order.price,
                                    counterparty=client_session.login)
            order_book_changes = order_book.on_new_order(new_order)
            order_book.apply_order_book_changes(order_book_changes)
            self.apply_order_book_changes_in_storage(order_book_changes)
            logger.debug(f"Changes to be applied:\n{str(order_book_changes)}")
        except KeyError:
            instrument_identifier = create_order.instrument_identifier
            logger.warning(f"Order book related to instrument identifier [{instrument_identifier}] does not exist")

    def apply_order_book_changes_in_storage(self, order_book_changes):
        if self.storage is None:
            logger.warning("Storage is not initialized")
            return
        for order_to_add in order_book_changes.order_to_add:
            logger.info(f"Order to add [{str(order_to_add)}]")
            self.storage.insert_order(order_to_add)
        for order_to_remove in order_book_changes.order_to_remove:
            logger.info(f"Order to remove [{str(order_to_remove)}]")
            self.storage.delete_order(order_to_remove)
        for deal_to_add in order_book_changes.deals_to_add:
            logger.info(f"Deal to add [{str(deal_to_add)}]")
            self.storage.insert_deal(deal_to_add)

    def get_order_books(self) -> Dict[int, OrderBook]:
        return self.order_books

    def initialize_order_books(self, referential):
        logger.trace("Initializing order books")
        # TODO: use generator
        for instrument in referential.instruments:
            self.order_books[instrument.identifier] = OrderBook(instrument.identifier)
        logger.trace(f"[{len(referential)}] order books are initialized")

    def handle_readable_client(self, **kwargs):
        client_session = self.client_sessions[kwargs['sock']]
        decoded_objects, client_session.received_buffer = self.marshaller.decode_buffer(client_session.received_buffer)
        for decoded_object in decoded_objects:
            try:
                self.handle_callbacks[decoded_object[0]](decoded_object[1], client_session.sock)
            except Exception as exception:
                logger.error(f"Matching engine, handle_readable_client failed [{exception}]")
                logger.exception(exception)
            except LogonRejected as exception:
                logger.info(f"[{client_session.login}] logon attempt from [{client_session.peer_name}] is rejected. "
                            f"Reason [{exception.reason}]")
                self.remove_client_socket(client_session.sock)
                break
            except OrderRejected as exception:
                logger.error(f"[{client_session.login}] order attempt from [{client_session.peer_name}] is rejected. "
                             f"Reason [{exception.reason}]")
                self.remove_client_socket(client_session.sock)
                break
        if len(decoded_objects) == 0:
            logger.info("--- No decoded messages ---")
