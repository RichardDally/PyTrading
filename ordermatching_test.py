import unittest
from way import Way
from order import Order
from currency import Currency
from orderbook import OrderBook
from instrument import Instrument

class TestOrderMatching(unittest.TestCase):
    book = None
    currency = None
    instrument = None

    def setUp(self):
        self.book = OrderBook()
        self.currency = Currency.get_available()[0]
        self.instrument = Instrument(0, 'Carrefour', self.currency, 'FR0000120172')

    def validate_one_matching(self, attackingOrder, attackedOrder):
        self.book.on_new_order(attackedOrder)
        matching = self.book.get_matching_orders(attackingOrder)
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0], attackedOrder)

    def test_buy_greater_than_sell(self):
        attackingOrder = Order(Way.BUY, self.instrument, 10, 40.0, 'Trader1')
        attackedOrder = Order(Way.SELL, self.instrument, 10, 38.0, 'Trader2')
        self.validate_one_matching(attackingOrder, attackedOrder)

    def test_buy_equal_to_sell(self):
        attackingOrder = Order(Way.BUY, self.instrument, 10, 40.0, 'Trader1')
        attackedOrder = Order(Way.SELL, self.instrument, 10, 40.0, 'Trader2')
        self.validate_one_matching(attackingOrder, attackedOrder)

    def test_sell_greater_than_buy(self):
        attackingOrder = Order(Way.SELL, self.instrument, 10, 40.0, 'Trader1')
        attackedOrder = Order(Way.BUY, self.instrument, 10, 42.0, 'Trader2')
        self.validate_one_matching(attackingOrder, attackedOrder)

    def test_sell_equal_to_buy(self):
        attackingOrder = Order(Way.SELL, self.instrument, 10, 40.0, 'Trader1')
        attackedOrder = Order(Way.BUY, self.instrument, 10, 40.0, 'Trader2')
        self.validate_one_matching(attackingOrder, attackedOrder)

if __name__ == '__main__':
    unittest.main()
