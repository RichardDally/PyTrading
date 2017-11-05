from orderway import Buy
from createorder import CreateOrder
from tcpclient import TcpClient


class OrderHandler(TcpClient):
    def __init__(self, marshaller, host, port):
        TcpClient.__init__(self, host, port)
        self.marshaller = marshaller
        self.referential = None
        self.handle_callbacks = {}

    def on_connect(self):
        create_order = CreateOrder(way=Buy(),
                                   price=42.0,
                                   quantity=1.0,
                                   instrument_identifier=1)
        encoded_create_order = self.marshaller.encode_create_order(create_order)
        self.output_message_stacks[self.server_socket].append(encoded_create_order)

    def on_read_from_server(self):
        decoded_messages_count, self.server_buffer = self.marshaller.decode_buffer(self.server_buffer,
                                                                                   self.handle_callbacks)
        if decoded_messages_count == 0:
            print('--- No decoded messages ---')
