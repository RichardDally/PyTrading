import unittest
from pytrading.core.instrument import Instrument
from pytrading.core.referential import Referential


class TestReferential(unittest.TestCase):
    instrument = None

    def setUp(self):
        self.instrument = Instrument(identifier=0, name='Carrefour', isin='FR0000120172', currency_identifier=0)

    def test_length(self):
        referential = Referential()
        self.assertEqual(len(referential), 0)
        referential.add_instrument(self.instrument)
        self.assertEqual(len(referential), 1)


if __name__ == '__main__':
    unittest.main()
