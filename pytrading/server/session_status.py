from enum import Enum


class SessionStatus(Enum):
    Handshaking = 1
    Authenticated = 2
    Disconnecting = 3
