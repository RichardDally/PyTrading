class Instrument:
    id = None
    name = None
    isin = None
    currencyId = None

    def __init__(self, id, name, isin, currencyId):
        self.id = id
        self.name = name
        self.isin = isin
        self.currencyId = currencyId

    def __str__(self):
        return '{} {} {} {}'.format(self.id, self.name, self.currencyId, self.isin)
