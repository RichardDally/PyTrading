from instrument import Instrument
from referential import Referential

currencies = {0 : 'EUR', 1 : 'USD'}
instruments = {0 : Instrument(id=0, name='Carrefour', isin='FR0000120172', currencyId=0),
               1 : Instrument(id=1, name='Societe Generale', isin='FR0000130809', currencyId=0)
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
