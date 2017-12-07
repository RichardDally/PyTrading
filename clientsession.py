class ClientSession:
    def __init__(self, status, sock, peer_name):
        self.status = status
        self.login = None
        self.password = None
        self.sock = sock
        self.peer_name = peer_name
