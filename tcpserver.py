import errno
import select
import socket
import logging
import traceback
from abc import ABCMeta, abstractmethod


class ClosedConnection(BaseException):
    """ Client socket connection has been closed """


class TcpServer:
    __metaclass__ = ABCMeta

    def __init__(self, port):
        self.logger = logging.getLogger(__name__)
        self.port = port
        self.select_timeout = 0.5
        self.listener = None
        self.inputs = []
        self.outputs = []
        self.message_stacks = {}

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
        print('Removing client [{}]'.format(sock.getpeername()))
        if sock in self.outputs:
            self.outputs.remove(sock)
        if sock in self.inputs:
            self.inputs.remove(sock)
        sock.close()
        if sock in self.message_stacks:
            del self.message_stacks[sock]

    def accept_connection(self):
        sock, _ = self.listener.accept()
        sock.setblocking(0)
        self.inputs.append(sock)
        self.outputs.append(sock)
        self.on_accept_connection(sock)

    @abstractmethod
    def on_accept_connection(self, sock):
        pass

    @abstractmethod
    def handle_readable_client(self, sock):
        pass

    def process_sockets(self):
        r, w, e = select.select(self.inputs, self.outputs, self.inputs, self.select_timeout)
        self.handle_readable(r)
        self.handle_writable(w)
        self.handle_exceptional(e)

    # FLAG SOCKETS TO REMOVE
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

    def handle_writable(self, writable):
        for sock in writable:
            remove_socket = True
            try:
                sent_messages = 0
                while len(self.message_stacks[sock]) > 0:
                    next_message = self.message_stacks[sock].pop(0)
                    sock.send(next_message)
                    sent_messages += 1
                    #print('DEBUG {}'.format(next_message))
                #print('[{}] messages were sent to [{}]'.format(sent_messages, sock.getpeername()))
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

