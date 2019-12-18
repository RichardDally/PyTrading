import unittest
from logon import Logon
from orderway import Buy, Sell
from serverorder import ServerOrder
from createorder import CreateOrder
from orderbook import OrderBook
from staticdata import StaticData
from referential import Referential
from staticdata import MessageTypes
from protobufserialization import ProtobufSerialization


class TestProtobufSerialization(unittest.TestCase):
    def setUp(self):
        self.instrument_identifier = 0
        self.marshaller = ProtobufSerialization()

    def test_logon(self):
        logon = Logon(login='Richard', password='MyUltraSecretPassword')
        encoded_logon = self.marshaller.encode_logon(logon=logon)
        message_type, body, _ = self.marshaller.decode_header(encoded_logon)
        decoded_logon = self.marshaller.decode_logon(body)
        self.assertEqual(message_type, MessageTypes.Logon.value)
        self.assertEqual(logon.__dict__, decoded_logon.__dict__)

    def test_empty_referential(self):
        empty_referential = Referential()
        encoded_referential = self.marshaller.encode_referential(empty_referential)
        message_type, body, _ = self.marshaller.decode_header(encoded_referential)
        decoded_referential = self.marshaller.decode_referential(body)
        self.assertEqual(message_type, MessageTypes.Referential.value)
        self.assertEqual(empty_referential.__dict__, decoded_referential.__dict__)

    def test_default_referential(self):
        referential = StaticData.get_default_referential()
        encoded_referential = self.marshaller.encode_referential(referential)
        message_type, body, _ = self.marshaller.decode_header(encoded_referential)
        decoded_referential = self.marshaller.decode_referential(body)
        self.assertEqual(message_type, MessageTypes.Referential.value)
        self.assertEqual(referential.__dict__, decoded_referential.__dict__)

    def test_empty_order_book(self):
        empty_order_book = OrderBook(StaticData.get_instrument(1).identifier)
        encoded_order_book = self.marshaller.encode_order_book(empty_order_book)
        message_type, body, _ = self.marshaller.decode_header(encoded_order_book)
        decoded_order_book = self.marshaller.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook.value)
        self.assertEqual(empty_order_book.__dict__, decoded_order_book.__dict__)

    def test_one_buy_order_book(self):
        simple_order_book = OrderBook(self.instrument_identifier)
        buy_order = ServerOrder(Buy(), self.instrument_identifier, quantity=100.0, price=10.0, counterparty='Trader1')
        simple_order_book.on_new_order(buy_order)
        encoded_order_book = self.marshaller.encode_order_book(simple_order_book)
        message_type, body, _ = self.marshaller.decode_header(encoded_order_book)
        decoded_order_book = self.marshaller.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook.value)
        self.assertEqual(encoded_order_book, self.marshaller.encode_order_book(decoded_order_book))

    def test_two_opposite_orders_in_order_book(self):
        order_book = OrderBook(self.instrument_identifier)
        orders = [ServerOrder(Buy(), self.instrument_identifier, quantity=100.0, price=9.0, counterparty='Trader1'),
                  ServerOrder(Sell(), self.instrument_identifier, quantity=100.0, price=10.0, counterparty='Trader2')]
        for order in orders:
            order_book.on_new_order(order)
        encoded_order_book = self.marshaller.encode_order_book(order_book)
        message_type, body, _ = self.marshaller.decode_header(encoded_order_book)
        decoded_order_book = self.marshaller.decode_order_book(body)
        self.assertEqual(message_type, MessageTypes.OrderBook.value)
        self.assertEqual(encoded_order_book, self.marshaller.encode_order_book(decoded_order_book))

    def test_simple_create_order(self):
        create_order = CreateOrder(way=Buy(), price=42.0, quantity=10.0, instrument_identifier=1)
        encoded_create_order = self.marshaller.encode_create_order(create_order=create_order)
        message_type, body, _ = self.marshaller.decode_header(encoded_create_order)
        decoded_create_order = self.marshaller.decode_create_order(body)
        self.assertEqual(message_type, MessageTypes.CreateOrder.value)
        self.assertEqual(create_order.__dict__, decoded_create_order.__dict__)
