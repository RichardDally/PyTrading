from loguru import logger


class Referential:
    def __init__(self):
        self.instruments = []

    def __cmp__(self, other):
        return self.__dict__ == other.__dict__

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __iter__(self):
        return self

    def __next__(self):
        for instrument in self.instruments:
            yield instrument

    def next(self):
        for instrument in self.instruments:
            yield instrument

    def __str__(self):
        return '\n'.join([str(instrument) for instrument in self.instruments])

    def __len__(self):
        return len(self.instruments)

    def add_instrument(self, instrument):
        logger.trace('Adding [{}] to referential'.format(instrument))
        self.instruments.append(instrument)

    def get_instruments(self):
        return self.instruments
