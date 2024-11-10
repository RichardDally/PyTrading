from pytrading import Logon
from pytrading import CreateOrder
from pytrading import TcpClient
from pytrading import ClosedConnection


class OrderSender(TcpClient):
    def __init__(self, login, password, marshaller, host, port):
        TcpClient.__init__(self, host, port)
        self.login = login
        self.password = password
        self.marshaller = marshaller
        self.handle_callbacks = {}

    def on_connect(self):
        logon = Logon(self.login, self.password)
        encoded_logon = self.marshaller.encode_logon(logon)
        self.output_message_stacks[self.server_socket].append(encoded_logon)

    def push_order(self, way, price, quantity, instrument_identifier):
        create_order = CreateOrder(way=way, price=price, quantity=quantity,
                                   instrument_identifier=instrument_identifier)
        encoded_create_order = self.marshaller.encode_create_order(create_order)
        if not self.server_socket:
            raise ClosedConnection
        self.output_message_stacks[self.server_socket].append(encoded_create_order)

    def on_read_from_server(self):
        decoded_messages_count, self.received_buffer = self.marshaller.decode_buffer(self.received_buffer,
                                                                                     self.handle_callbacks)
        if decoded_messages_count == 0:
            print("--- No decoded messages ---")
