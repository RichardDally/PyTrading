import logging
import socket
import pickle
from referential import Referential
from instrument import Instrument
from currency import Currency
from orderbook import OrderBook

class TradingServer:
    logger = logging.getLogger(__name__)
    referential = None
    orderBooks = None

    def __init__(self):
        self.initialize_referential()
        self.initialize_order_books()

    """ public """
    def start(self):
        listener = None
        clientSocket = None

        try:
            listener = socket.socket()
            host = socket.gethostname()
            port = 12345
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((host, port))

            print('Listening')
            listener.listen(1)
            clientSocket, addr = listener.accept()
            print('Got connection from', addr)
            self.send_referential(clientSocket)

        except KeyboardInterrupt, exception:
            print('Stopped by user')
        except Exception, exception:
        # TODO: catch other exceptions
            print(exception)

        if listener:
            listener.close()
        if clientSocket:
            clientSocket.close()

        print('Ok')

    """ private """
    def send_referential(self, clientSocket):
        self.logger.debug('Sending referential to [{}]'.format(clientSocket))
        clientSocket.send(pickle.dumps(self.referential))

    """ private """
    def initialize_referential(self):
        self.logger.debug('Loading referential')
        self.referential = Referential.get_default()
        self.logger.debug('Referential is loaded')

    """ private """
    def initialize_order_books(self):
        self.logger.debug('Initializing order books')
        self.orderBooks = {}
        # TODO: use generator
        for instrument in self.referential.instruments:
            self.orderBooks[instrument.id] = OrderBook(instrument)
        self.logger.debug('[{}] order books are initialized'.format(len(self.referential)))

if __name__ == '__main__':
    logging.basicConfig(filename='TradingServer.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    server = TradingServer()
    server.start()
