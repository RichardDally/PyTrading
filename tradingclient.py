import logging
import socket
import pickle
from instrument import Instrument
from referential import Referential

class TradingClient:
    logger = logging.getLogger(__name__)
    referential = None

    def __init__(self):
        self.initialize_referential()

    """ public """
    def start(self):
        serverSocket = None

        try:
            serverSocket = socket.socket()
            host = socket.gethostname()
            port = 12345

            print('Connecting')
            serverSocket.connect((host, port))
            self.receive_referential(serverSocket)

        except KeyboardInterrupt:
            print('Stopped by user')
        except Exception, exception:
        # TODO: catch other exceptions
            print(exception)

        if serverSocket:
            serverSocket.close()

        print('Ok')

    """ private """
    def receive_referential(self, serverSocket):
        self.logger.debug('Receiving referential from [{}]'.format(serverSocket))
        buffer = serverSocket.recv(4096)
        self.referential = pickle.loads(buffer)

    """ private """
    def initialize_referential(self):
        self.logger.debug('Loading referential')
        self.referential = Referential.get_default()
        self.logger.debug('Referential is loaded')

if __name__ == '__main__':
    client = TradingClient()
    client.start()
