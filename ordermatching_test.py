import unittest
from way import Way
from order import Order
from orderbook import OrderBook
from instrument import Instrument


class TestOrderMatching(unittest.TestCase):
    book = None
    instrument = None

    def setUp(self):
        self.instrument = Instrument(identifier=0, name='Carrefour', isin='FR0000120172', currency_identifier=0)
        self.book = OrderBook(self.instrument)

    def validate_one_matching(self, attacking_order, attacked_order):
        self.book.on_new_order(attacked_order)
        matching_orders = self.book.get_matching_orders(attacking_order)
        self.assertEqual(len(matching_orders), 1)
        self.assertEqual(matching_orders[0], attacked_order)

    def test_buy_price_greater_than_sell(self):
        attacking_order = Order(Way.BUY, self.instrument, 10, 40.0, 'Trader1')
        attacked_order = Order(Way.SELL, self.instrument, 10, 38.0, 'Trader2')
        self.validate_one_matching(attacking_order, attacked_order)

    def test_buy_price_equal_to_sell(self):
        attacking_order = Order(Way.BUY, self.instrument, 10, 40.0, 'Trader1')
        attacked_order = Order(Way.SELL, self.instrument, 10, 40.0, 'Trader2')
        self.validate_one_matching(attacking_order, attacked_order)

    def test_sell_price_greater_than_buy(self):
        attacking_order = Order(Way.SELL, self.instrument, 10, 40.0, 'Trader1')
        attacked_order = Order(Way.BUY, self.instrument, 10, 42.0, 'Trader2')
        self.validate_one_matching(attacking_order, attacked_order)

    def test_sell_price_equal_to_buy(self):
        attacking_order = Order(Way.SELL, self.instrument, 10, 40.0, 'Trader1')
        attacked_order = Order(Way.BUY, self.instrument, 10, 40.0, 'Trader2')
        self.validate_one_matching(attacking_order, attacked_order)

    def test_one_full_execution(self):
        quantity = 10
        price = 42.0
        attacking_order = Order(Way.SELL, self.instrument, quantity, price, 'Trader1')
        attacked_order = Order(Way.BUY, self.instrument, quantity, price, 'Trader2')
        self.book.on_new_order(attacked_order)
        self.book.on_new_order(attacking_order)
        self.assertEqual(self.book.count_bids(), 0)
        self.assertEqual(self.book.count_asks(), 0)
        self.assertEqual(attacking_order.executed_quantity, quantity)
        self.assertEqual(attacked_order.executed_quantity, quantity)
        self.assertEqual(attacking_order.get_remaining_quantity(), 0)
        self.assertEqual(attacked_order.get_remaining_quantity(), 0)

    def test_one_partial_execution(self):
        attacking_quantity = 20
        attacked_quantity = 10
        price = 42.0
        attacking_order = Order(Way.BUY, self.instrument, attacking_quantity, price, 'Trader1')
        attacked_order = Order(Way.SELL, self.instrument, attacked_quantity, price, 'Trader2')
        self.book.on_new_order(attacked_order)
        self.book.on_new_order(attacking_order)
        self.assertEqual(self.book.count_bids(), 1)
        self.assertEqual(self.book.count_asks(), 0)
        self.assertEqual(attacking_order.executed_quantity, attacking_quantity - attacked_quantity)
        self.assertEqual(attacked_order.executed_quantity, attacked_quantity)
        self.assertEqual(attacking_order.get_remaining_quantity(), attacking_quantity - attacked_quantity)
        self.assertEqual(attacked_order.get_remaining_quantity(), 0)

    def test_multiple_partial_executions(self):
        attacking_quantity = 50
        attacked_quantity = 10
        price = 42.0
        attacking_order = Order(Way.BUY, self.instrument, attacking_quantity, price, 'Trader1')
        attacked_orders = []
        for _ in list(range(5)):
            attacked_order = Order(Way.SELL, self.instrument, attacked_quantity, price, 'Trader2')
            attacked_orders.append(attacked_order)
            self.book.on_new_order(attacked_order)
        self.book.on_new_order(attacking_order)
        self.assertEqual(self.book.count_bids(), 0)
        self.assertEqual(self.book.count_asks(), 0)
        self.assertEqual(attacking_order.executed_quantity, attacking_quantity)
        self.assertEqual(attacking_order.get_remaining_quantity(), 0)
        for attacked_order in attacked_orders:
            self.assertEqual(attacked_order.executed_quantity, attacked_quantity)
            self.assertEqual(attacked_order.get_remaining_quantity(), 0)

if __name__ == '__main__':
    unittest.main()
