from orderway import Buy
from createorder import CreateOrder
from tcpclient import TcpClient


class OrderHandler(TcpClient):
    def __init__(self, marshaller, host, port):
        TcpClient.__init__(self, host, port)
        self.marshaller = marshaller
        self.referential = None
        self.handle_callbacks = {}

    def on_read_from_server(self):
        decoded_messages_count, self.server_buffer = self.marshaller.decode_buffer(self.server_buffer,
                                                                                   self.handle_callbacks)
        if decoded_messages_count == 0:
            print('--- No decoded messages ---')

    def on_write_to_server(self, sock):
        pass
