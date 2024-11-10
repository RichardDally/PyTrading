import time
from pytrading import pretty_timestamp
from pytrading import generate_unique_identifier


class ServerOrder:
    """ A server order contains full details about the order """

    def __init__(self, way, instrument_identifier, quantity, price, counterparty,
                 identifier=None, timestamp=None,
                 canceled_quantity=0.0, executed_quantity=0.0):
        if not counterparty:
            raise ValueError("Counterparty not set")
        self.identifier = identifier if identifier is not None else generate_unique_identifier()
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
            raise ValueError(f"Remaining quantity [{remaining_quantity}] cannot be negative")
        return remaining_quantity

    def __str__(self):
        """
        Note remaining quantity is always displayed
        """
        return f"Id [{self.instrument_identifier}] " \
               f"[{str(self.way)}] " \
               f"[{self.get_remaining_quantity()}] @ [{self.price}] " \
               f"from [{self.counterparty}] " \
               f"[{pretty_timestamp(self.timestamp)}]"

    def pretty(self, remaining_quantity: bool) -> str:
        quantity_to_display = self.get_remaining_quantity() if remaining_quantity else self.quantity
        return f"Instrument id [{self.instrument_identifier}] " \
               f"[{str(self.way)}] [{quantity_to_display}] @ [{self.price}] " \
               f"from [{self.counterparty}] [{pretty_timestamp(self.timestamp)}]"

    def __cmp__(self, other):
        return self.__dict__ == other.__dict__

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
