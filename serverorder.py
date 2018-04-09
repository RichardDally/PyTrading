import time


class Counter:
    def __init__(self):
        self.value = 0

    def get_value(self):
        value = self.value
        self.value += 1
        return value


counter = Counter()


class ServerOrder:
    """ A server order contains full details about the order """

    def __init__(self, way, instrument_identifier, quantity, price, counterparty,
                 identifier=counter.get_value(), timestamp=None,
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
            raise Exception('Remaining quantity cannot be negative')
        return remaining_quantity

    def __str__(self):
        return '{} {} {} @ {} from {} ({})'.format(str(self.way),
                                                   self.instrument_identifier,
                                                   self.get_remaining_quantity(),
                                                   self.price,
                                                   self.counterparty,
                                                   self.timestamp)

    def __cmp__(self, other):
        return self.__dict__ == other.__dict__

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
