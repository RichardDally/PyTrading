class SessionStatus:
    Handshaking = 1
    Authenticated = 2
    Disconnecting = 3

    def __init__(self, status):
        self.status = status
