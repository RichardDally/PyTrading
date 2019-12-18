import unittest
from orderway import OrderWay, Buy, Sell, WayEnum
from exceptions import InvalidWay


class TestOrderWay(unittest.TestCase):
    def setUp(self):
        pass

    def test_buy_way(self):
        order_way = Buy()
        self.assertEqual(order_way.way, WayEnum.BUY)
        self.assertEqual(order_way.__dict__, Buy().__dict__)

    def test_sell_way(self):
        order_way = Sell()
        self.assertEqual(order_way.way, WayEnum.SELL)
        self.assertEqual(order_way.__dict__, Sell().__dict__)

    def test_invalid_way(self):
        wrong_way_value = 42
        with self.assertRaises(InvalidWay):
            OrderWay(way=wrong_way_value)
