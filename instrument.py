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

    def get_available(self):
        return [Instrument(0, 'Carrefour', euroCurrency, 'FR0000120172')]