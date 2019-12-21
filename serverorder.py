import time
import uuid


class ServerOrder:
    """ A server order contains full details about the order """

    def __init__(self, way, instrument_identifier, quantity, price, counterparty,
                 identifier=uuid.uuid4().bytes, timestamp=None,
                 canceled_quantity=0.0, executed_quantity=0.0):
        if not counterparty:
            raise Exception('Counterparty not set')
        self.identifier = identifier
        self.way = way
        self.instrument_identifier = instrument_identifier
        self.quantity = quantity
        self.canceled_quantity = canceled_quantity
        self.executed_quantity = executed_quantity
        self.price = price
        self.counterparty = counterparty
        if timestamp:
            self.timestamp = timestamp
        else:
            # TODO: improve timestamp precision to milliseconds
            self.timestamp = int(time.time())

    def get_remaining_quantity(self):
        remaining_quantity = self.quantity - self.executed_quantity - self.canceled_quantity
        if remaining_quantity < 0.0:
            raise Exception("Remaining quantity cannot be negative")
        return remaining_quantity

    def __str__(self):
        return f"{str(self.way)} {self.instrument_identifier} {self.get_remaining_quantity()} @ {self.price} " \
               f"from {self.counterparty} ({self.timestamp})"

    def __cmp__(self, other):
        return self.__dict__ == other.__dict__

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
