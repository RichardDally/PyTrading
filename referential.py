import logging


class Referential:
    logger = logging.getLogger(__name__)
    instruments = None

    def __init__(self):
        self.instruments = []

    def __iter__(self):
        return self

    # TODO: implement correctly
    #def next(self):
    #     for instrument in self.instruments:
    #         yield instrument

    # TODO: implement correctly
    # def __next__(self):
    #     for instrument in self.instruments:
    #         yield instrument

    def __str__(self):
        return '\n'.join([str(instrument) for instrument in self.instruments])

    def __len__(self):
        return len(self.instruments)

    def add_instrument(self, instrument):
        self.logger.debug('Adding [{}] to referential'.format(instrument))
        self.instruments.append(instrument)

    def get_instruments(self):
        return self.instruments
