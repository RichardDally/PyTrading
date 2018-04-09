import errno
import select
import socket
import logging
import traceback
from abc import ABCMeta, abstractmethod


class TcpClient:
    __metaclass__ = ABCMeta

    def __init__(self, host, port):
        self.logger = logging.getLogger(__name__)
        self.server_socket = None
        self.received_buffer = bytearray()
        self.host = host
        self.port = port
        self.select_timeout = 0.5
        self.listener = None
        self.inputs = []
        self.outputs = []
        self.output_message_stacks = {}
        self.r = None
        self.w = None

    @staticmethod
    def close_sockets(socket_container):
        for sock in socket_container:
            if sock:
                sock.close()

    def cleanup(self):
        TcpClient.close_sockets(self.inputs)
        TcpClient.close_sockets(self.outputs)

    def is_connected(self):
        return self.server_socket is not None

    @abstractmethod
    def on_connect(self):
        pass

    def connect(self):
        if self.server_socket:
            raise Exception("Already connected...")
        self.server_socket = socket.socket()
        self.server_socket.settimeout(10)
        self.logger.info('Connecting on [{0}:{1}]'.format(self.host, self.port))
        self.server_socket.connect((self.host, self.port))
        self.inputs.append(self.server_socket)
        # TODO: investigate why this goes to 100% CPU
        self.output_message_stacks[self.server_socket] = []
        self.on_connect()

    def remove_server_socket(self):
        self.logger.info('Removing server socket [{}]'.format(self.server_socket.getsockname()))
        if self.server_socket in self.outputs:
            self.outputs.remove(self.server_socket)
        if self.server_socket in self.inputs:
            self.inputs.remove(self.server_socket)
        self.server_socket.close()
        if self.server_socket in self.r:
            self.r.remove(self.server_socket)
        if self.server_socket in self.w:
            self.w.remove(self.server_socket)
        self.server_socket = None

    @abstractmethod
    def on_read_from_server(self):
        pass

    def process_sockets(self):
        if len(self.output_message_stacks[self.server_socket]):
            self.outputs.append(self.server_socket)

        self.r, self.w, _ = select.select(self.inputs, self.outputs, self.inputs, self.select_timeout)

        for sock in self.r:
            self.generic_handle(handler=self.read_from_server, sock=sock)

        for sock in self.w:
            self.generic_handle(handler=self.write_to_server, sock=sock)

    def read_from_server(self, **kwargs):
        sock = kwargs.get('sock')
        data = sock.recv(8192)
        if data:
            self.logger.debug('Adding server data ({}) to received buffer'.format(len(data)))
            self.received_buffer += data
            self.on_read_from_server()
        else:
            self.logger.info('Server [{}] closed its socket'.format(sock.getpeername()))
            self.remove_server_socket()

    def write_to_server(self, **kwargs):
        sock = kwargs.get('sock')
        while len(self.output_message_stacks[sock]) > 0:
            next_message = self.output_message_stacks[sock].pop(0)
            sock.send(next_message)
        self.outputs.remove(sock)

    def generic_handle(self, **kwargs):
        try:
            kwargs['handler'](**kwargs)
            return
        except KeyboardInterrupt:
            raise
        except KeyError:
            pass
        except socket.error as exception:
            if exception.errno not in (errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN):
                self.logger.error('Server connection lost, unhandled errno [{}]'.format(exception.errno))
                self.logger.error(traceback.print_exc())
        except Exception as exception:
            self.logger.error('generic_handle: {}'.format(exception))
            self.logger.error(traceback.print_exc())

        self.remove_server_socket()
