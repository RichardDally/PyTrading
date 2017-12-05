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
        self.client_sessions = {}
        self.inputs = []
        self.outputs = []
        self.output_message_stacks = {}
        # TODO: only one server buffer for every clients is wrong
        self.received_buffer = bytearray()
        self.r = None
        self.w = None

    @staticmethod
    def close_sockets(socket_container):
        for sock in socket_container:
            if sock:
                sock.close()

    def cleanup(self):
        TcpServer.close_sockets(self.inputs)
        TcpServer.close_sockets(self.outputs)

    def remove_client_socket(self, sock):
        print('Removing client socket [{}]'.format(sock.getsockname()))
        if sock in self.outputs:
            self.outputs.remove(sock)
        if sock in self.inputs:
            self.inputs.remove(sock)
        sock.close()
        if sock in self.output_message_stacks:
            del self.output_message_stacks[sock]
        if sock in self.r:
            self.r.remove(sock)
        if sock in self.w:
            self.w.remove(sock)

    def accept_connection(self):
        sock, _ = self.listener.accept()
        sock.setblocking(0)
        self.inputs.append(sock)
        self.outputs.append(sock)
        self.on_accept_connection(sock=sock)

    @abstractmethod
    def on_accept_connection(self, **kwargs):
        pass

    @abstractmethod
    def handle_readable_client(self, **kwargs):
        pass

    def process_sockets(self):
        self.r, self.w, _ = select.select(self.inputs, self.outputs, self.inputs, self.select_timeout)

        for sock in self.r:
            if sock is self.listener:
                self.accept_connection()
            else:
                self.generic_handle(handler=self.handle_readable, sock=sock)

        for sock in self.w:
            self.generic_handle(handler=self.handle_writable, sock=sock)

    def generic_handle(self, **kwargs):
        try:
            kwargs['handler'](**kwargs)
            return
        except KeyboardInterrupt:
            raise
        except ClosedConnection:
            pass
        except socket.error as exception:
            if exception.errno not in (errno.ECONNRESET, errno.ENOTCONN, errno.EWOULDBLOCK):
                print('Client connection lost, unhandled errno [{}]'.format(exception.errno))
                print(traceback.print_exc())
        except Exception as exception:
            print('generic_handle: {}'.format(exception))
            print(traceback.print_exc())
        self.remove_client_socket(kwargs['sock'])

    def handle_readable(self, **kwargs):
        sock = kwargs['sock']
        data = sock.recv(8192)
        if not data:
            raise ClosedConnection
        self.received_buffer += data
        self.handle_readable_client(**kwargs)

    def handle_writable(self, **kwargs):
        sock = kwargs.get('sock')
        while len(self.output_message_stacks[sock]) > 0:
            next_message = self.output_message_stacks[sock].pop(0)
            sock.send(next_message)

    def listen(self):
        self.listener = socket.socket()
        self.listener.setblocking(0)
        host = socket.gethostname()
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((host, self.port))
        self.listener.listen(5)
        self.inputs.append(self.listener)
