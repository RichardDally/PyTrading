import logging
import socket
from referential import Referential
from instrument import Instrument
from currency import Currency
from orderbook import OrderBook

class TradingServer:
    logger = logging.getLogger(__name__)
    referential = Referential()
    orderBooks = {}

    def __init__(self):
        self.load_instruments()

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
            clientSocket.send('Thank you for connecting')
            clientSocket.close()
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
    def load_instruments(self):
        euroCurrency = Currency.get_available()[0]
        instrumentId = 0
        instrument = Instrument(id=instrumentId, name='Carrefour', currency=euroCurrency, isin='FR0000120172')
        self.referential.add_instrument(instrument)
        self.orderBooks[instrumentId] = instrument
        self.logger.debug('Instruments are loaded')

if __name__ == '__main__':
    server = TradingServer()
    server.start()
