import unittest
from way import Way
from createorder import CreateOrder
from order import Order
from orderbook import OrderBook
from staticdata import StaticData
from referential import Referential
from staticdata import MessageTypes
from simpleserialization import SimpleSerialization


class TestSimpleSerialization(unittest.TestCase):
    def setUp(self):
        self.instrument_identifier = 1
        self.marshaller = SimpleSerialization()

    def test_empty_referential(self):
        empty_referential = Referential()
        encoded_referential = self.marshaller.encode_referential(empty_referential)
        message_type, body, _ = self.marshaller.decode_header(encoded_referential)
        decoded_referential = self.marshaller.decode_referential(body)
        self.assertEqual(message_type, MessageTypes.Referential)
        self.assertEqual(empty_referential.__dict__, decoded_referential.__dict__)

    def test_default_referential(self):
        referential = StaticData.get_default_referential()
        encoded_referential = self.marshaller.encode_referential(referential)
        message_type, body, _ = self.marshaller.decode_header(encoded_referential)
        decoded_referential = self.marshaller.decode_referential(body)
        self.assertEqual(message_type, MessageTypes.Referential)
        self.assertEqual(referential.__dict__, decoded_referential.__dict__)

    def test_empty_order_book(self):
        empty_order_book = OrderBook(self.instrument_identifier)
        encoded_order_book = self.marshaller.encode_order_book(empty_order_book)
        message_type, body, _ = self.marshaller.decode_header(encoded_order_book)
        decoded_order_book = self.marshaller.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook)
        self.assertEqual(empty_order_book.__dict__, decoded_order_book.__dict__)

    def test_one_buy_order_book(self):
        simple_order_book = OrderBook(self.instrument_identifier)
        buy_order = Order(Way.BUY, self.instrument_identifier, quantity=100.0, price=10.0, counterparty='Trader1')
        simple_order_book.add_order(buy_order)
        encoded_order_book = self.marshaller.encode_order_book(simple_order_book)
        message_type, body, _ = self.marshaller.decode_header(encoded_order_book)
        decoded_order_book = self.marshaller.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook)
        self.assertEqual(encoded_order_book, self.marshaller.encode_order_book(decoded_order_book))

    def test_two_opposite_orders_in_order_book(self):
        order_book = OrderBook(self.instrument_identifier)
        orders = [Order(Way.BUY, self.instrument_identifier, quantity=100.0, price=9.0, counterparty='Trader1'),
                  Order(Way.SELL, self.instrument_identifier, quantity=100.0, price=10.0, counterparty='Trader2')]
        for order in orders:
            order_book.add_order(order)
        encoded_order_book = self.marshaller.encode_order_book(order_book)
        message_type, body, _ = self.marshaller.decode_header(encoded_order_book)
        decoded_order_book = self.marshaller.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook)
        self.assertEqual(encoded_order_book, self.marshaller.encode_order_book(decoded_order_book))

    def test_simple_create_order(self):
        create_order = CreateOrder(way=Way.BUY, price=42.0, quantity=10.0, instrument_identifier=1)
        encoded_create_order = self.marshaller.encode_create_order(create_order=create_order)
        message_type, body, _ = self.marshaller.decode_header(encoded_create_order)
        decoded_create_order = self.marshaller.decode_create_order(body)
        self.assertEqual(message_type, MessageTypes.CreateOrder)
        self.assertEqual(create_order.__dict__, decoded_create_order.__dict__)


if __name__ == '__main__':
    unittest.main()
