class LogonRejected(BaseException):
    """ Client logon attempt is rejected """
    def __init__(self, reason):
        self.reason = reason


class OrderRejected(BaseException):
    """ Order creation is rejected """
    def __init__(self, reason):
        self.reason = reason


class NotEnoughBytes(BaseException):
    """ Unable to decode message, available bytes are less than required """


class InvalidWay(BaseException):
    """ Way must be equal to BUY or SELL """


class ClosedConnection(BaseException):
    """ Client socket connection has been closed """
