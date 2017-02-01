class Instrument:
    id = None
    name = None
    currency = None
    isin = None

    def __init__(self, id, name, currency, isin):
        self.id = id
        self.name = name
        self.currency = currency
        self.isin = isin

    def __str__(self):
        return self.name
