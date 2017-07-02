class Instrument:
    def __init__(self, identifier, name, isin, currency_identifier):
        self.identifier = identifier
        self.name = name
        self.isin = isin
        self.currency_identifier = currency_identifier

    def __str__(self):
        return '{} {} {} {}'.format(self.identifier, self.name, self.currency_identifier, self.isin)
