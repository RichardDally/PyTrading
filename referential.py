import logging
from instrument import Instrument

class Referential:
    logger = logging.getLogger(__name__)
    instruments = []

    def __init__(self):
        pass

    def add_instrument(self, instrument):
        self.logger.debug('Adding [{}] to referential'.format(instrument))
        self.instruments.append(instrument)

    def get_instruments(self):
        return self.instruments
