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
        self.server_buffer = bytearray()
        self.host = host
        self.port = port
        self.select_timeout = 0.5
        self.listener = None
        self.inputs = []
        self.outputs = []
        self.r = None
        self.w = None

    @staticmethod
    def close_sockets(socket_container):
        for sock in socket_container:
            if sock:
                print('Removing server socket [{}]'.format(sock.getpeername()))
                sock.close()

    def cleanup(self):
        TcpClient.close_sockets(self.inputs)
        TcpClient.close_sockets(self.outputs)

    def is_connected(self):
        return self.server_socket is not None

    def connect(self):
        if self.server_socket:
            raise Exception("Already connected...")
        self.server_socket = socket.socket()
        self.server_socket.settimeout(10)
        print('Connecting on [{0}:{1}]'.format(self.host, self.port))
        self.server_socket.connect((self.host, self.port))
        self.inputs.append(self.server_socket)

    def remove_server_socket(self):
        print('Removing server socket [{}]'.format(self.server_socket.getpeername()))
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

    def read_from_server(self, sock):
        data = sock.recv(8192)
        if data:
            self.logger.debug('Adding server data ({}) to buffer'.format(len(data)))
            self.server_buffer += data
            self.on_read_from_server()
        else:
            print('Server closed its socket')
            self.remove_server_socket()

    @abstractmethod
    def on_read_from_server(self):
        pass

    @abstractmethod
    def on_write_to_server(self, sock):
        pass

    def process_sockets(self):
        self.r, self.w, _ = select.select(self.inputs, self.outputs, self.inputs, self.select_timeout)

        for sock in self.r:
            self.generic_handle(self.read_from_server, sock)

        for sock in self.w:
            self.generic_handle(self.on_write_to_server, sock)

    def generic_handle(self, handler, sock):
        try:
            handler(sock)
            return
        except KeyboardInterrupt:
            raise
        except KeyError:
            pass
        except socket.error as exception:
            if exception.errno not in (errno.ECONNRESET, errno.ENOTCONN):
                print('Server connection lost, unhandled errno [{}]'.format(exception.errno))
                print(traceback.print_exc())
        except Exception as exception:
            print('generic_handle: {}'.format(exception))
            print(traceback.print_exc())

        self.remove_server_socket()
