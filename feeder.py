from tcpserver import TcpServer
from staticdata import StaticData
from sessionstatus import SessionStatus
from loguru import logger


class Feeder(TcpServer):
    """
    Feeder is a server that streams referential and order books
    """
    def __init__(self, marshaller, port):
        TcpServer.__init__(self, port)
        self.marshaller = marshaller
        self.referential = None
        self.initialize_referential()

    def get_referential(self):
        return self.referential

    def initialize_referential(self):
        logger.info("Loading referential")
        self.referential = StaticData.get_default_referential()
        logger.info(f"Referential is loaded (size [{len(self.referential)}])")

    def on_accept_connection(self, **kwargs):
        """
        Send the referential to incoming client
        Order books will be send afterwards
        """
        client_session = kwargs["client_session"]
        logger.info(f"Feeder got connection from [{client_session.peer_name}]")
        # No authentication for Feed (for the moment)
        client_session.status = SessionStatus.Authenticated
        logger.debug(f"Push encoded referential to [{client_session.peer_name}]")
        client_session.output_message_stack.append(self.marshaller.encode_referential(self.referential))

    def handle_readable_client(self, **kwargs):
        raise NotImplementedError("handle_readable_client")

    def send_one_peer_order_books(self, **kwargs):
        sock = kwargs["sock"]
        client_session = self.client_sessions[sock]
        logger.trace(f"Adding message to [{client_session.peer_name}] message queue")
        for encoded_order_book in kwargs['encoded_order_books']:
            client_session.output_message_stack.append(encoded_order_book)
        logger.trace(f"Message queue size [{len(client_session.output_message_stack)}] for [{client_session.peer_name}]")

    def send_all_order_books(self, order_books):
        """
        1) Encode once all books
        2) Enqueue messages for all clients
        3) Actual sending is done later in TcpServer.handle_writable
        """
        if len(self.inputs) == 1 and self.inputs[0] is self.listener:
            logger.trace("Nothing to send...")
            return
        encoded_order_books = []
        for _, order_book in order_books.items():
            encoded_order_books.append(self.marshaller.encode_order_book(order_book))
        for sock in self.inputs:
            if sock is self.listener:
                continue
            self.generic_handle(handler=self.send_one_peer_order_books,
                                sock=sock,
                                encoded_order_books=encoded_order_books)
