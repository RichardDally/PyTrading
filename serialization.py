import capnp
import referential_capnp
from instrument import Instrument
from referential import Referential

class Serialization:
    @staticmethod
    def encode_referential(referential):
        referentialMessage = referential_capnp.Referential.new_message()
        instrumentsSize = len(referential)
        if instrumentsSize:
            instrumentList = referentialMessage.init('instruments', instrumentsSize)
            for index, instrument in enumerate(referential.get_instruments()):
                instrumentList[index].id = instrument.id
                instrumentList[index].name = instrument.name
                instrumentList[index].isin = instrument.isin
                instrumentList[index].currencyId = instrument.currencyId
        return referentialMessage

    @staticmethod
    def decode_referential(encodedReferential):
        referential = Referential()
        referentialMessage = referential_capnp.Referential.from_bytes(encodedReferential)
        for decodedInstrument in referentialMessage.instruments:
            instrument = Instrument(id=decodedInstrument.id,
                                    name=decodedInstrument.name,
                                    isin=decodedInstrument.isin,
                                    currencyId=decodedInstrument.currencyId)
            referential.add_instrument(instrument)
        return referential
