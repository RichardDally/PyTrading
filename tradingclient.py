import logging
import socket
from instrument import Instrument
from referential import Referential

class TradingClient:
    logger = logging.getLogger(__name__)
    referential = None

    def __init__(self):
        self.initialize_referential()

    """ public """
    def start(self):
        clientSocket = None

        try:
            clientSocket = socket.socket()
            host = socket.gethostname()
            port = 12345

            print('Connecting')
            clientSocket.connect((host, port))
            buffer = clientSocket.recv(1024)
            print(buffer)
        except KeyboardInterrupt:
            print('Stopped by user')
        except Exception, exception:
            print(exception)

        if clientSocket:
            clientSocket.close()

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
