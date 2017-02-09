import logging
import socket
from instrument import Instrument
from referential import Referential

class TradingClient:
    logger = logging.getLogger(__name__)
    referential = Referential()

    def __init__(self):
        pass

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

if __name__ == '__main__':
    client = TradingClient()
    client.start()
