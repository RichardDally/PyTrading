import unittest
from orderway import OrderWay, Buy, Sell, InvalidWay, WayEnum


class TestOrderWay(unittest.TestCase):
    def setUp(self):
        pass

    def test_buy_way(self):
        order_way = Buy()
        self.assertEqual(order_way.way, WayEnum.BUY)
        self.assertEqual(order_way, Buy())

    def test_sell_way(self):
        order_way = Sell()
        self.assertEqual(order_way.way, WayEnum.SELL)
        self.assertEqual(order_way, Sell())

    def test_invalid_way(self):
        wrong_way_value = 42
        with self.assertRaises(InvalidWay) as context:
            OrderWay(way=wrong_way_value)
        self.assertTrue(wrong_way_value in context.exception)


if __name__ == '__main__':
    unittest.main()
