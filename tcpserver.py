import errno
import select
import socket
from loguru import logger
from exceptions import ClosedConnection
from clientsession import ClientSession
from sessionstatus import SessionStatus
from abc import ABCMeta, abstractmethod


class TcpServer:
    """
    Generic TCP server to handle multiple connections using select syscall.
    """
    __metaclass__ = ABCMeta

    def __init__(self, port):
        self.port = port
        self.select_timeout = 0.5
        self.listener = None
        self.client_sessions = {}
        self.inputs = []
        self.outputs = []
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
        client_session = self.client_sessions.pop(sock)
        logger.info(f"Removing client socket [{client_session.peer_name}] from port [{self.port}]")
        if sock in self.outputs:
            self.outputs.remove(sock)
        if sock in self.inputs:
            self.inputs.remove(sock)
        if sock in self.r:
            self.r.remove(sock)
        if sock in self.w:
            self.w.remove(sock)
        sock.close()

    def accept_connection(self):
        sock, _ = self.listener.accept()
        sock.setblocking(False)
        self.inputs.append(sock)
        self.outputs.append(sock)
        client_session = ClientSession(status=SessionStatus.Handshaking,
                                       sock=sock,
                                       peer_name=sock.getpeername())
        self.client_sessions[sock] = client_session
        self.on_accept_connection(client_session=client_session)

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
        """
        Exception safe generic method to avoid exception handling duplicates
        """
        try:
            kwargs['handler'](**kwargs)
            return
        except KeyboardInterrupt:
            raise
        except ClosedConnection:
            pass
        except socket.error as exception:
            if exception.errno not in (errno.ECONNRESET, errno.ENOTCONN, errno.EWOULDBLOCK):
                logger.warning(f"Client connection lost, unhandled errno [{exception.errno}]")
                logger.exception(exception)
        except Exception as exception:
            logger.error(f"generic_handle: {exception}")
            logger.exception(exception)
        self.remove_client_socket(kwargs['sock'])

    def handle_readable(self, **kwargs):
        sock = kwargs["sock"]
        client_session = self.client_sessions[sock]
        data = client_session.sock.recv(8192)
        if not data:
            raise ClosedConnection
        client_session.received_buffer += data
        self.handle_readable_client(**kwargs)

    def handle_writable(self, **kwargs):
        sock = kwargs['sock']
        client_session = self.client_sessions[sock]
        while len(client_session.output_message_stack) > 0:
            next_message = client_session.output_message_stack.pop(0)
            client_session.sock.send(next_message)

    def listen(self):
        self.listener = socket.socket()
        self.listener.setblocking(False)
        host = socket.gethostname()
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((host, self.port))
        self.listener.listen(5)
        self.inputs.append(self.listener)
