import logging
import capnp
import referential_capnp
from currency import Currency
from instrument import Instrument

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

    def encode(self):
        referentialMessage = referential_capnp.Referential.new_message()
        instrumentsSize = len(self.instruments)
        if instrumentsSize:
            instrumentList = referentialMessage.init('instruments', instrumentsSize)
            for index, instrument in enumerate(self.instruments):
                instrumentList[index].id = instrument.id
                instrumentList[index].name = instrument.name
                instrumentList[index].isin = instrument.isin
                instrumentList[index].currencyId = instrument.currencyId
        return referentialMessage

    def decode(self, encodedMessage):
        referential = referential_capnp.Referential.from_bytes(encodedMessage)
        for instrument in referential.instruments:
            instr = Instrument(id=instrument.id, name=instrument.name, isin=instrument.isin, currencyId=instrument.currencyId)
            self.add_instrument(instr)
        print(self)
