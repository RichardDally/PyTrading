class ClientSession:
    def __init__(self, status, sock, peer_name):
        self.status = status
        self.login = None
        self.password = None
        self.sock = sock
        self.peer_name = peer_name
        self.output_message_stack = []
        self.received_buffer = bytearray()

    def __str__(self):
        return '[{}] known as [{}] status [{}]'.format(self.login,
                                                       self.peer_name,
                                                       self.status.name)
