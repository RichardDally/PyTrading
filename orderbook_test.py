import unittest
from orderway import Buy, Sell
from order import Order
from orderbook import OrderBook
from instrument import Instrument


class TestOrderBook(unittest.TestCase):
    def setUp(self):
        self.instrument = Instrument(identifier=0, name='Carrefour', isin='FR0000120172', currency_identifier=0)
        self.book = OrderBook(self.instrument.identifier)

    def test_count_bids(self):
        buy_order = Order(Buy(), self.instrument.identifier, 50, 42.0, 'Trader1')
        self.assertEqual(self.book.count_bids(), 0)
        self.book.on_new_order(buy_order)
        self.assertEqual(self.book.count_bids(), 1)

    def test_count_asks(self):
        sell_order = Order(Sell(), self.instrument.identifier, 50, 42.0, 'Trader1')
        self.assertEqual(self.book.count_asks(), 0)
        self.book.on_new_order(sell_order)
        self.assertEqual(self.book.count_asks(), 1)

    def test_get_bids(self):
        bids = self.book.get_bids()
        self.assertEqual(len(bids), 0)

    def test_get_asks(self):
        asks = self.book.get_asks()
        self.assertEqual(len(asks), 0)

    def test_two_orders_no_match(self):
        buy_order = Order(Buy(), self.instrument.identifier, 50, 40.0, 'Trader1')
        sell_order = Order(Sell(), self.instrument.identifier, 50, 42.0, 'Trader2')
        self.book.on_new_order(buy_order)
        self.book.on_new_order(sell_order)
        self.assertEqual(self.book.count_bids(), 1)
        self.assertEqual(self.book.count_asks(), 1)

    def test_four_stacked_orders_no_match(self):
        orders = [Order(Buy(), self.instrument.identifier, 50, 40.0, 'Trader1'),
                  Order(Buy(), self.instrument.identifier, 50, 40.0, 'Trader1'),
                  Order(Sell(), self.instrument.identifier, 50, 42.0, 'Trader2'),
                  Order(Sell(), self.instrument.identifier, 50, 42.0, 'Trader2')]
        for order in orders:
            self.book.on_new_order(order)
        self.assertEqual(self.book.count_bids(), 2)
        self.assertEqual(self.book.count_asks(), 2)

    def test_fifo_matching_orders(self):
        """ Ensure FIFO matching is enforced """
        orders = [Order(Buy(), self.instrument.identifier, 50, 40.0, 'Trader1', timestamp=1),
                  Order(Buy(), self.instrument.identifier, 50, 40.0, 'Trader2', timestamp=2),
                  Order(Sell(), self.instrument.identifier, 50, 40.0, 'Trader3', timestamp=3)]
        for order in orders:
            self.book.on_new_order(order)
        self.assertEqual(self.book.count_bids(), 1)
        self.assertEqual(self.book.count_asks(), 0)
        self.assertEqual(self.book.get_bids()[0].timestamp, 2)
        self.assertEqual(self.book.get_bids()[0].counterparty, 'Trader2')


if __name__ == '__main__':
    unittest.main()
