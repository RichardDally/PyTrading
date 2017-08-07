import time
import errno
import logging
import socket
import select
import traceback
from staticdata import StaticData
from orderbook import OrderBook


class ClosedConnection(BaseException):
    """ Client socket connection has been closed """

class TcpServer:
    def __init__(self, port):
        self.logger = logging.getLogger(__name__)
        self.port = port
        self.select_timeout = 1
        self.listener = None
        self.inputs = []
        self.outputs = []
        self.message_stacks = {}
        self.client_addresses = {}

    @staticmethod
    def close_sockets(socket_container):
        for sock in socket_container:
            if sock:
                sock.close()

    def cleanup(self):
        self.listener.close()
        TcpServer.close_sockets(self.inputs)
        TcpServer.close_sockets(self.outputs)

    def remove_client_socket(self, sock):
        if sock in self.client_addresses:
            print('Removing client [{}]'.format(self.client_addresses[sock]))
            del self.client_addresses[sock]
        if sock in self.outputs:
            self.outputs.remove(sock)
        if sock in self.inputs:
            self.inputs.remove(sock)
        sock.close()
        if sock in self.message_stacks:
            del self.message_stacks[sock]

    def accept_connection(self):
        sock, client_address = self.listener.accept()
        self.client_addresses[sock] = client_address
        sock.setblocking(0)
        self.inputs.append(sock)
        self.on_accept_connection(sock)

    def on_accept_connection(self, sock):
        raise NotImplementedError

    def handle_readable(self, readable):
        for sock in readable:
            if sock is self.listener:
                self.accept_connection()
            else:
                remove_socket = True
                try:
                    self.handle_readable_client(sock)
                    remove_socket = False
                except ClosedConnection:
                    print('DEBUG CLOSED CONNECTION')
                    pass
                except KeyboardInterrupt:
                    raise
                except socket.error as exception:
                    if exception.errno not in (errno.ECONNRESET, errno.ENOTCONN):
                        print('Client connection lost, unhandled errno [{}]'.format(exception.errno))
                        print(traceback.print_exc())
                except Exception as exception:
                    print('handle_readable: {}'.format(exception))
                    print(traceback.print_exc())
                finally:
                    if remove_socket:
                        self.remove_client_socket(sock)

    def handle_readable_client(self, sock):
        raise NotImplementedError

    def handle_writable(self, writable):
        for sock in writable:
            remove_socket = True
            try:
                while len(self.message_stacks[sock]) > 0:
                    next_message = self.message_stacks[sock].pop(0)
                    sock.send(next_message)
                    print('DEBUG {}'.format(next_message))
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

    def listen(self):
        self.listener = socket.socket()
        self.listener.setblocking(0)
        host = socket.gethostname()
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((host, self.port))
        self.listener.listen(5)
        self.inputs.append(self.listener)

    def process_sockets(self):
        r, w, e = select.select(self.inputs, self.outputs, self.inputs, self.select_timeout)
        self.handle_readable(r)
        self.handle_writable(w)
        self.handle_exceptional(e)


class Feeder(TcpServer):
    def __init__(self, marshaller, port):
        TcpServer.__init__(self, port)
        self.marshaller = marshaller
        self.referential = None
        self.initialize_referential()

    def get_referential(self):
        return self.referential

    def initialize_referential(self):
        self.logger.debug('Loading referential')
        self.referential = StaticData.get_default_referential()
        self.logger.debug('Referential is loaded')

    def on_accept_connection(self, sock):
        message_stack = []
        message = self.marshaller.encode_referential(self.referential)
        message_stack.append(message)
        self.message_stacks[sock] = message_stack

        client_address = None
        if sock in self.client_addresses:
            client_address = self.client_addresses[sock]
        print('Feeder got connection from [{}]'.format(client_address))

    def handle_readable_client(self, sock):
        data = sock.recv(8192)
        if not data:
            raise ClosedConnection

    def distribute_order_books(self, order_books):
        encoded_order_books = []
        for _, order_book in order_books.items():
            encoded_order_books.append(self.marshaller.encode_order_book(order_book))
        for sock in self.inputs:
            if sock is self.listener:
                continue
            self.logger.debug('Adding message to [{}]  message queue'.format(sock))
            for encoded_order_book in encoded_order_books:
                self.message_stacks[sock].append(encoded_order_book)
            self.logger.debug('Message queue size [{}] for [{}]'.format(len(self.message_stacks[sock]), sock))

        #print('SELF INPUTS {}'.format(len(self.inputs)))
        #print('ORDER BOOKS {}'.format(len(order_books)))
        #print('ENCODED ORDER BOOKS {}'.format(len(encoded_order_books)))

class MatchingEngine(TcpServer):
    def __init__(self, referential, marshaller, port):
        TcpServer.__init__(self, port)
        self.marshaller = marshaller
        self.referential = referential
        self.order_books = {}
        self.initialize_order_books()

    def get_order_books(self):
        return self.order_books

    def initialize_order_books(self):
        self.logger.debug('Initializing order books')
        # TODO: use generator
        for instrument in self.referential.instruments:
            self.order_books[instrument.identifier] = OrderBook(instrument.identifier)
        self.logger.debug('[{}] order books are initialized'.format(len(self.referential)))

    def on_accept_connection(self, sock):
        client_address = None
        if sock in self.client_addresses:
            client_address = self.client_addresses[sock]
        print('Matching engine got connection from [{}]'.format(client_address))


class TradingServer2:
    def __init__(self, marshaller, feeder_port, matching_engine_port, uptime_in_seconds):
        self.feeder = Feeder(marshaller=marshaller, port=feeder_port)
        self.matching_engine = MatchingEngine(referential=self.feeder.get_referential(), marshaller=marshaller, port=matching_engine_port)
        self.start_time = None
        self.stop_time = None
        if uptime_in_seconds:
            self.start_time = time.time()
            self.stop_time = self.start_time + uptime_in_seconds

    def reached_uptime(self):
        if self.stop_time:
            return time.time() >= self.stop_time
        return False

    def print_listen_messages(self):
        if self.start_time and self.stop_time:
            print('Feeder listening on port [{}] for [{}] seconds'.format(self.feeder.port,
                                                                          self.stop_time - self.start_time))
            print('Matching engine listening on port [{}] for [{}] seconds'.format(self.matching_engine.port,
                                                                                   self.stop_time - self.start_time))
        else:
            print('Feeder listening on port [{}]'.format(self.feeder.port))
            print('Matching engine listening on port [{}]'.format(self.matching_engine.port))

    def start(self):
        try:
            self.feeder.listen()
            self.matching_engine.listen()
            self.print_listen_messages()

            while not self.reached_uptime():
                self.matching_engine.process_sockets()
                self.feeder.process_sockets()
                self.feeder.distribute_order_books(self.matching_engine.get_order_books())

        except KeyboardInterrupt:
            print('Stopped by user')
        except socket.error as exception:
            print('Socket error [{}]'.format(exception))
            print(traceback.print_exc())
        finally:
            self.feeder.cleanup()
            self.matching_engine.cleanup()

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
        #server = TradingServer(CapnpSerialization, uptime_in_seconds=None)
        server = TradingServer2(feeder_port=42001, matching_engine_port=42000, marshaller=CapnpSerialization, uptime_in_seconds=None)
        server.start()
    except ImportError as error:
        print('Unable to start trading server. [{}]'.format(error))
