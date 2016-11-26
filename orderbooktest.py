import unittest                                                                                                                                                                                                    
from way import Way
from order import Order
from currency import Currency
from orderbook import OrderBook
from instrument import Instrument

class TestOrderBook(unittest.TestCase):
    book = None
    currency = None
    instrument = None

    def setUp(self):
        self.book = OrderBook()
        self.currency = Currency.get_available()[0]
        self.instrument = Instrument(0, 'Carrefour', self.currency, 'FR0000120172')

    def test_one_buy_order(self):
        order = Order(Way.BUY, self.instrument, 50, 42.0, 'Trader1')
        self.book.on_new_order(order)
        self.assertEqual(self.book.count_buy_orders(), 1)
        self.assertEqual(self.book.count_sell_orders(), 0)

    def test_one_sell_order(self):
        order = Order(Way.SELL, self.instrument, 50, 42.0, 'Trader1')
        self.book.on_new_order(order)
        self.assertEqual(self.book.count_buy_orders(), 0)
        self.assertEqual(self.book.count_sell_orders(), 1)

    def test_two_orders_no_match(self):
        buyorder = Order(Way.BUY, self.instrument, 50, 40.0, 'Trader1')
        sellorder = Order(Way.SELL, self.instrument, 50, 42.0, 'Trader2')
        self.book.on_new_order(buyorder)
        self.book.on_new_order(sellorder)
        self.assertEqual(self.book.count_buy_orders(), 1)
        self.assertEqual(self.book.count_sell_orders(), 1)
	
	def test_two_orders_no_match(self):
        buyorder = Order(Way.BUY, self.instrument, 50, 40.0, 'Trader1')
        sellorder = Order(Way.SELL, self.instrument, 50, 42.0, 'Trader2')
        self.book.on_new_order(buyorder)
        self.book.on_new_order(sellorder)
        self.assertEqual(self.book.count_buy_orders(), 1)
        self.assertEqual(self.book.count_sell_orders(), 1)

    def test_four_stacked_orders_no_match(self):
        orders = [Order(Way.BUY, self.instrument, 50, 40.0, 'Trader1'),
                  Order(Way.BUY, self.instrument, 50, 40.0, 'Trader1'),
                  Order(Way.SELL, self.instrument, 50, 42.0, 'Trader2'),
                  Order(Way.SELL, self.instrument, 50, 42.0, 'Trader2')]
        for order in orders:
            self.book.on_new_order(order)
        self.assertEqual(self.book.count_buy_orders(), 2)
        self.assertEqual(self.book.count_sell_orders(), 2)

if __name__ == '__main__':
    unittest.main()