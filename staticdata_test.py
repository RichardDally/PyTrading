import unittest
from staticdata import StaticData


class TestReferential(unittest.TestCase):
    def test_default_referential(self):
        referential = StaticData.get_default_referential()
        self.assertIsNotNone(referential)
        self.assertGreater(len(referential), 0)

    def test_at_least_one_instrument(self):
        instrument = StaticData.get_instrument(1)
        self.assertIsNotNone(instrument)

    def test_at_least_one_currency(self):
        currency = StaticData.get_currency(1)
        self.assertIsNotNone(currency)

if __name__ == '__main__':
    unittest.main()
