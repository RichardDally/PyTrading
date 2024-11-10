class Instrument:
    def __init__(self, identifier: int, name: str, isin: str, currency_identifier: int):
        self.identifier = identifier
        self.name = name
        self.isin = isin
        self.currency_identifier = currency_identifier

    def __str__(self):
        return '{} {} {} {}'.format(self.identifier, self.name, self.currency_identifier, self.isin)

    def __cmp__(self, other):
        return self.__dict__ == other.__dict__

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
