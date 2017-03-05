import time
from way import Way

class Order:
    way = None
    quantity = None
    price = None
    instrument = None
    timestamp = None

    def __init__(self, way, instrument, quantity, price, counterparty):
        self.way = way
        self.instrument = instrument
        self.quantity = quantity
        self.canceledquantity = 0.0
        self.executedquantity = 0.0
        self.price = price
        self.counterparty = counterparty
        self.timestamp = time.time()

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
