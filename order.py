import time
from way import Way


class Counter:
    def __init__(self):
        self.value = 0

    def get_value(self):
        value = self.value
        self.value += 1
        return value
counter = Counter()


class Order:
    def __init__(self, way, instrument_identifier, quantity, price, counter_party, identifier=counter.get_value(), timestamp=time.time()):
        self.identifier = identifier
        self.way = way
        self.instrument_identifier = instrument_identifier
        self.quantity = quantity
        self.canceled_quantity = 0.0
        self.executed_quantity = 0.0
        self.price = price
        self.counter_party = counter_party
        self.timestamp = timestamp

    def get_remaining_quantity(self):
        remaining_quantity = self.quantity - self.executed_quantity - self.canceled_quantity
        if remaining_quantity < 0.0:
            raise Exception('Remaining quantity cannot be negative')
        return remaining_quantity

    def __str__(self):
        way = None
        if self.way == Way.BUY:
            way = 'BUY'
        elif self.way == Way.SELL:
            way = 'SELL'
        return '{} {} {} @ {} ({})'.format(way,
                                           self.instrument_identifier,
                                           self.get_remaining_quantity(),
                                           self.price,
                                           self.timestamp)
