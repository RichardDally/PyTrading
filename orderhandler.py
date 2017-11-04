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
        pass

    def on_write_to_server(self, sock):
        pass
