import pytest
from orderway import Buy, Sell
from referential import Referential
from staticdata import StaticData
from staticdata import MessageTypes
from orderbook import OrderBook
from serverorder import ServerOrder
from createorder import CreateOrder
from logon import Logon
from simpleserialization import SimpleSerialization
from protobufserialization import ProtobufSerialization


@pytest.mark.parametrize("instrument_identifier", [1])
@pytest.mark.parametrize('marshaller', [SimpleSerialization(), ProtobufSerialization()])
class TestSerialization:
    def test_logon(self, instrument_identifier, marshaller):
        logon = Logon(login='Richard', password='MyUltraSecretPassword')
        encoded_logon = marshaller.encode_logon(logon=logon)
        message_type, body, _ = marshaller.decode_header(encoded_logon)
        decoded_logon = marshaller.decode_logon(body)
        assert message_type == MessageTypes.Logon.value
        assert logon.__dict__ == decoded_logon.__dict__

    def test_empty_referential(self, instrument_identifier, marshaller):
        empty_referential = Referential()
        encoded_referential = marshaller.encode_referential(empty_referential)
        message_type, body, _ = marshaller.decode_header(encoded_referential)
        decoded_referential = marshaller.decode_referential(body)
        assert message_type == MessageTypes.Referential.value
        assert empty_referential.__dict__ == decoded_referential.__dict__

    def test_default_referential(self, instrument_identifier, marshaller):
        referential = StaticData.get_default_referential()
        encoded_referential = marshaller.encode_referential(referential)
        message_type, body, _ = marshaller.decode_header(encoded_referential)
        decoded_referential = marshaller.decode_referential(body)
        assert message_type == MessageTypes.Referential.value
        assert referential.__dict__ == decoded_referential.__dict__

    def test_empty_order_book(self, instrument_identifier, marshaller):
        empty_order_book = OrderBook(instrument_identifier)
        encoded_order_book = marshaller.encode_order_book(empty_order_book)
        message_type, body, _ = marshaller.decode_header(encoded_order_book)
        decoded_order_book = marshaller.decode_order_book(body)
        assert message_type == MessageTypes.OrderBook.value
        assert empty_order_book.__dict__ == decoded_order_book.__dict__

    def test_one_buy_order_book(self, instrument_identifier, marshaller):
        simple_order_book = OrderBook(instrument_identifier)
        buy_order = ServerOrder(Buy(), instrument_identifier, quantity=100.0, price=10.0, counterparty='Trader1')
        simple_order_book.add_order(buy_order)
        encoded_order_book = marshaller.encode_order_book(simple_order_book)
        message_type, body, _ = marshaller.decode_header(encoded_order_book)
        decoded_order_book = marshaller.decode_order_book(body)
        assert message_type == MessageTypes.OrderBook.value
        assert encoded_order_book == marshaller.encode_order_book(decoded_order_book)

    def test_two_opposite_orders_in_order_book(self, instrument_identifier, marshaller):
        order_book = OrderBook(instrument_identifier)
        orders = [ServerOrder(Buy(), instrument_identifier, quantity=100.0, price=9.0, counterparty='Trader1'),
                  ServerOrder(Sell(), instrument_identifier, quantity=100.0, price=10.0, counterparty='Trader2')]
        for order in orders:
            order_book.add_order(order)
        encoded_order_book = marshaller.encode_order_book(order_book)
        message_type, body, _ = marshaller.decode_header(encoded_order_book)
        decoded_order_book = marshaller.decode_order_book(body)
        assert message_type == MessageTypes.OrderBook.value
        assert encoded_order_book == marshaller.encode_order_book(decoded_order_book)

    def test_simple_create_order(self, instrument_identifier, marshaller):
        create_order = CreateOrder(way=Buy(), price=42.0, quantity=10.0, instrument_identifier=1)
        encoded_create_order = marshaller.encode_create_order(create_order=create_order)
        message_type, body, _ = marshaller.decode_header(encoded_create_order)
        decoded_create_order = marshaller.decode_create_order(body)
        assert message_type == MessageTypes.CreateOrder.value
        assert create_order.__dict__ == decoded_create_order.__dict__
