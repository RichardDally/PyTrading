import unittest
from instrument import Instrument
from staticdata import StaticData
from referential import Referential


class TestReferential(unittest.TestCase):
    instrument = None

    def setUp(self):
        self.instrument = Instrument(identifier=0, name='Carrefour', isin='FR0000120172', currency_identifier=0)

    def test_length(self):
        referential = Referential()
        self.assertEqual(len(referential), 0)
        referential.add_instrument(self.instrument)
        self.assertEqual(len(referential), 1)

    def test_get_default_is_not_empty(self):
        referential = StaticData.get_default_referential()
        self.assertGreater(len(referential), 0)

if __name__ == '__main__':
    unittest.main()
