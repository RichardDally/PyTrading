import time
from way import Way
from staticdata import StaticData

class Counter:
    def __init__(self):
        self.value = 0

    def get_value(self):
        value = self.value
        self.value += 1
        return value
counter = Counter()

class Order:
    id = None
    way = None
    quantity = None
    price = None
    instrument = None
    counterparty = None
    timestamp = None

    def __init__(self, way, instrument, quantity, price, counterparty, id = counter.get_value(), timestamp=time.time()):
        self.id = id
        self.way = way
        self.instrument = instrument
        self.quantity = quantity
        self.canceledquantity = 0.0
        self.executedquantity = 0.0
        self.price = price
        self.counterparty = counterparty
        self.timestamp = timestamp

    def get_remaining_quantity(self):
        remainingQuantity = self.quantity - self.executedquantity - self.canceledquantity
        assert (remainingQuantity >= 0.0), 'Remaining quantity cannot be negative'
        return remainingQuantity

    def __str__(self):
        way = None
        if self.way == Way.BUY:
            way = 'BUY'
        elif self.way == Way.SELL:
            way = 'SELL'

        currency = StaticData.get_currency(self.instrument.currencyId)
        return '{} {} {} {} @ {} ({})'.format(way, self.instrument.name, self.get_remaining_quantity(), currency, self.price, self.timestamp)
