import unittest
from way import Way
from order import Order
from orderbook import OrderBook
from staticdata import StaticData
from referential import Referential
from staticdata import MessageTypes
from simpleserialization import SimpleSerialization


class TestSimpleSerialization(unittest.TestCase):
    def setUp(self):
        self.instrument = StaticData.get_instrument(0)

    def test_empty_referential(self):
        empty_referential = Referential()
        encoded_referential = SimpleSerialization.encode_referential(empty_referential)
        message_type, body, new_offset = SimpleSerialization.decode_header(encoded_referential)
        decoded_referential = SimpleSerialization.decode_referential(body)
        self.assertEqual(empty_referential.__dict__, decoded_referential.__dict__)

    def test_default_referential(self):
        referential = StaticData.get_default_referential()
        encoded_referential = SimpleSerialization.encode_referential(referential)
        message_type, body, _ = SimpleSerialization.decode_header(encoded_referential)
        decoded_referential = SimpleSerialization.decode_referential(body)
        self.assertEqual(message_type, MessageTypes.Referential)
        self.assertEqual(referential.__dict__, decoded_referential.__dict__)

    def test_empty_order_book(self):
        empty_order_book = OrderBook(StaticData.get_instrument(0).identifier)
        encoded_order_book = SimpleSerialization.encode_order_book(empty_order_book)
        message_type, body, new_offset = SimpleSerialization.decode_header(encoded_order_book)
        decoded_order_book = SimpleSerialization.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook)
        self.assertEqual(empty_order_book.__dict__, decoded_order_book.__dict__)

    def test_simple_order_book(self):
        simple_order_book = OrderBook(self.instrument.identifier)
        buy_order = Order(Way.BUY, self.instrument.identifier, 100.0, 10.0, 'Trader1')
        simple_order_book.add_order(buy_order)
        encoded_order_book = SimpleSerialization.encode_order_book(simple_order_book)
        message_type, body, new_offset = SimpleSerialization.decode_header(encoded_order_book)
        decoded_order_book = SimpleSerialization.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook)
        self.assertEqual(encoded_order_book, SimpleSerialization.encode_order_book(decoded_order_book))

if __name__ == '__main__':
    unittest.main()