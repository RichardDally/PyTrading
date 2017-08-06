import time
import errno
import logging
import socket
import select
import traceback
from staticdata import StaticData
from orderbook import OrderBook


class TradingServer:
    def __init__(self, s, uptime_in_seconds=None):
        self.s = s
        self.logger = logging.getLogger(__name__)
        self.referential = None
        self.order_books = {}
        self.inputs = []
        self.outputs = []
        self.listener = None
        self.message_stacks = {}
        self.initialize_referential()
        self.initialize_order_books()
        self.startTime = None
        self.stopTime = None
        if uptime_in_seconds:
            self.startTime = time.time()
            self.stopTime = self.startTime + uptime_in_seconds

    def broadcast(self):
        encoded_order_books = []
        for _, order_book in self.order_books.items():
            encoded_order_books.append(self.s.encode_order_book(order_book))

        for s in self.inputs:
            if s is self.listener:
                continue
            self.logger.debug('Adding message to [{}]  message queue'.format(s))
            for encoded_order_book in encoded_order_books:
                self.message_stacks[s].append(encoded_order_book)
            self.logger.debug('Message queue size [{}] for [{}]'.format(len(self.message_stacks[s]), s))

    def start(self):
        try:
            self.listener = socket.socket()
            self.listener.setblocking(0)
            host = socket.gethostname()
            port = 12345
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listener.bind((host, port))

            if self.startTime and self.stopTime:
                print('Listening port [{}] for [{}] seconds'.format(port, self.stopTime - self.startTime))
            else:
                print('Listening port [{}]'.format(port))

            self.listener.listen(5)
            self.inputs.append(self.listener)

            while self.inputs:
                timeout_in_seconds = 1
                r, w, e = select.select(self.inputs, self.outputs, self.inputs, timeout_in_seconds)
                self.handle_readable(r)
                self.handle_writable(w)
                self.handle_exceptional(e)

                self.broadcast()

                if self.reached_uptime():
                    print('Time is up')
                    break

        except KeyboardInterrupt:
            print('Stopped by user')
        except socket.error as exception:
            print('Socket error [{}]'.format(exception))
            print(traceback.print_exc())
        finally:
            for input_socket in self.inputs:
                if input_socket:
                    input_socket.close()
        print('Server ends')

    def reached_uptime(self):
        if self.stopTime:
            return time.time() >= self.stopTime
        return False

    def initialize_referential(self):
        self.logger.debug('Loading referential')
        self.referential = StaticData.get_default_referential()
        self.logger.debug('Referential is loaded')

    def initialize_order_books(self):
        self.logger.debug('Initializing order books')
        # TODO: use generator
        for instrument in self.referential.instruments:
            self.order_books[instrument.identifier] = OrderBook(instrument.identifier)
        self.logger.debug('[{}] order books are initialized'.format(len(self.referential)))

    def accept_connection(self):
        sock, client_address = self.listener.accept()
        print('Got connection from [{}]'.format(client_address))
        sock.setblocking(0)
        self.inputs.append(sock)

        message_stack = []
        message = self.s.encode_referential(self.referential)
        message_stack.append(message)

        self.message_stacks[sock] = message_stack
        self.outputs.append(sock)

    def remove_client_socket(self, sock):
        if sock in self.outputs:
            self.outputs.remove(sock)
        if sock in self.inputs:
            self.inputs.remove(sock)
        sock.close()
        if sock in self.message_stacks:
            del self.message_stacks[sock]

    def handle_readable(self, readable):
        for sock in readable:
            if sock is self.listener:
                self.accept_connection()
            else:
                remove_socket = True
                try:
                    data = sock.recv(8192)
                    if data:
                        remove_socket = False
                except KeyboardInterrupt:
                    raise
                except socket.error as exception:
                    if exception.errno not in (errno.ECONNRESET, errno.ENOTCONN):
                        print('Client connection lost, unhandled errno [{}]'.format(exception.errno))
                        print(traceback.print_exc())
                except Exception as exception:
                    print('handle_readable: {}'.format(__name__, exception))
                    print(traceback.print_exc())
                finally:
                    if remove_socket:
                        self.remove_client_socket(sock)

    def handle_writable(self, writable):
        for sock in writable:
            remove_socket = True
            try:
                while len(self.message_stacks[sock]) > 0:
                    next_message = self.message_stacks[sock].pop(0)
                    sock.send(next_message)
                remove_socket = False
            except KeyboardInterrupt:
                raise
            except KeyError:
                pass
            except socket.error as exception:
                if exception.errno not in (errno.ECONNRESET, errno.ENOTCONN):
                    print('Client connection lost, unhandled errno [{}]'.format(exception.errno))
                    print(traceback.print_exc())
            except Exception as exception:
                print('handle_writable: {}'.format(exception))
                print(traceback.print_exc())
            finally:
                if remove_socket:
                    self.remove_client_socket(sock)

    def handle_exceptional(self, exceptional):
        for sock in exceptional:
            self.remove_client_socket(sock)


if __name__ == '__main__':
    logging.basicConfig(filename='TradingServer.log',
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    try:
        from capnpserialization import CapnpSerialization
        server = TradingServer(CapnpSerialization, uptime_in_seconds=None)
        server.start()
    except ImportError as error:
        print('Unable to start trading server. [{}]'.format(error))
