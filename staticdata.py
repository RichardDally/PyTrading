from instrument import Instrument
from referential import Referential


class MessageTypes:
    Referential = 1
    OrderBook = 2
    CreateOrder = 3


currencies = {1: 'EUR',
              2: 'USD'}

instruments = {1: Instrument(identifier=1, name='Carrefour', isin='FR0000120172', currency_identifier=1),
               2: Instrument(identifier=2, name='Societe Generale', isin='FR0000130809', currency_identifier=1)
               }


class StaticData:
    @staticmethod
    def get_currency(index):
        return currencies.get(index)

    @staticmethod
    def get_default_referential():
        referential = Referential()
        for _, instrument in instruments.items():
            referential.add_instrument(instrument)
        return referential

    @staticmethod
    def get_instrument(index):
        return instruments.get(index)
