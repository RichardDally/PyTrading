import unittest
from currency import Currency
from referential import Referential
from instrument import Instrument

class TestReferential(unittest.TestCase):
    currency = None
    instrument = None

    def setUp(self):
        self.currency = Currency.get_available()[0]
        self.instrument = Instrument(0, 'Carrefour', self.currency, 'FR0000120172')

    def test_length(self):
        referential = Referential()
        self.assertEqual(len(referential), 0)
        referential.add_instrument(self.instrument)
        self.assertEqual(len(referential), 1)

    def test_get_default_is_not_empty(self):
        referential = Referential.get_default()
        self.assertGreater(len(referential), 0)

if __name__ == '__main__':
    unittest.main()
