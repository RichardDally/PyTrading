import unittest
from way import Way
from order import Order
from orderbook import OrderBook
from staticdata import StaticData
from referential import Referential
from staticdata import MessageTypes
from protobufserialization import ProtobufSerialization


class TestProtobufSerialization(unittest.TestCase):
    def setUp(self):
        self.instrument_identifier = 0

    def test_empty_referential(self):
        empty_referential = Referential()
        encoded_referential = ProtobufSerialization.encode_referential(empty_referential)
        message_type, body, _ = ProtobufSerialization.decode_header(encoded_referential)
        decoded_referential = ProtobufSerialization.decode_referential(body)
        self.assertEqual(message_type, MessageTypes.Referential)
        self.assertEqual(empty_referential.__dict__, decoded_referential.__dict__)

    def test_default_referential(self):
        referential = StaticData.get_default_referential()
        encoded_referential = ProtobufSerialization.encode_referential(referential)
        message_type, body, _ = ProtobufSerialization.decode_header(encoded_referential)
        decoded_referential = ProtobufSerialization.decode_referential(body)
        self.assertEqual(message_type, MessageTypes.Referential)
        self.assertEqual(referential.__dict__, decoded_referential.__dict__)

    def test_empty_order_book(self):
        empty_order_book = OrderBook(StaticData.get_instrument(1).identifier)
        encoded_order_book = ProtobufSerialization.encode_order_book(empty_order_book)
        message_type, body, _ = ProtobufSerialization.decode_header(encoded_order_book)
        decoded_order_book = ProtobufSerialization.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook)
        self.assertEqual(empty_order_book.__dict__, decoded_order_book.__dict__)

    def test_one_buy_order_book(self):
        simple_order_book = OrderBook(self.instrument_identifier)
        buy_order = Order(Way.BUY, self.instrument_identifier, quantity=100.0, price=10.0, counterparty='Trader1')
        simple_order_book.add_order(buy_order)
        encoded_order_book = ProtobufSerialization.encode_order_book(simple_order_book)
        message_type, body, _ = ProtobufSerialization.decode_header(encoded_order_book)
        decoded_order_book = ProtobufSerialization.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook)
        self.assertEqual(encoded_order_book, ProtobufSerialization.encode_order_book(decoded_order_book))

    def test_two_opposite_orders_in_order_book(self):
        order_book = OrderBook(self.instrument_identifier)
        orders = [Order(Way.BUY, self.instrument_identifier, quantity=100.0, price=9.0, counterparty='Trader1'),
                  Order(Way.SELL, self.instrument_identifier, quantity=100.0, price=10.0, counterparty='Trader2')]
        for order in orders:
            order_book.add_order(order)
        encoded_order_book = ProtobufSerialization.encode_order_book(order_book)
        message_type, body, _ = ProtobufSerialization.decode_header(encoded_order_book)
        decoded_order_book = ProtobufSerialization.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook)
        self.assertEqual(encoded_order_book, ProtobufSerialization.encode_order_book(decoded_order_book))

if __name__ == '__main__':
    unittest.main()
