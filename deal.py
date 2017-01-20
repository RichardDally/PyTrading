class Deal:
    way = None
    quantity = None
    price = None
    instrument = None
    currency = None

    def __init__(self, way, quantity, price, instrument):
        self.way = way
        self.quantity = quantity
        self.price = price
        self.instrument = instrument
