from instrument import Instrument
from referential import Referential
from enum import Enum


class MessageTypes(Enum):
    Logon = 1
    Referential = 2
    OrderBook = 3
    CreateOrder = 4


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
