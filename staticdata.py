from instrument import Instrument
from referential import Referential


class MessageTypes:
    Referential = 'R'
    OrderBook = 'O'

currencies = {0: 'EUR',
              1: 'USD'}

instruments = {0: Instrument(identifier=0, name='Carrefour', isin='FR0000120172', currency_identifier=0),
               1: Instrument(identifier=1, name='Societe Generale', isin='FR0000130809', currency_identifier=0)
               }


class StaticData:
    @staticmethod
    def get_currency(index):
        return currencies.get(index)

    @staticmethod
    def get_default_referential():
        referential = Referential()
        referential.add_instrument(instruments[0])
        referential.add_instrument(instruments[1])
        return referential

    @staticmethod
    def get_instrument(index):
        return instruments.get(index)
