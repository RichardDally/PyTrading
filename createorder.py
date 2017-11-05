class CreateOrder:
    def __init__(self, way, quantity, price, instrument_identifier):
        self.way = way
        self.quantity = quantity
        self.price = price
        self.instrument_identifier = instrument_identifier

    def __str__(self):
        return 'NewOrder: {} instrument {} -> {}@{}'.format(str(self.way),
                                                            self.instrument_identifier,
                                                            self.quantity,
                                                            self.price)
