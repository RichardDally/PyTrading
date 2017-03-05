from instrument import Instrument
from referential import Referential

currencies = {0 : 'EUR', 1 : 'USD'}

class StaticData:
    @staticmethod
    def get_currency(index):
        return currencies.get(index)

    @staticmethod
    def get_default_referential():
        referential = Referential()
        referential.add_instrument(Instrument(id=0, name='Carrefour', isin='FR0000120172', currencyId=0))
        referential.add_instrument(Instrument(id=1, name='Societe Generale', isin='FR0000130809', currencyId=0))
        return referential
