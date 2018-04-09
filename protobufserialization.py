import struct
import logging
import orderbook_pb2
import referential_pb2
import createorder_pb2
import logon_pb2
from logon import Logon
from serverorder import ServerOrder
from orderway import OrderWay
from createorder import CreateOrder
from orderbook import OrderBook
from instrument import Instrument
from referential import Referential
from staticdata import MessageTypes
from serialization import Serialization
from exceptions import NotEnoughBytes


class ProtobufSerialization(Serialization):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.decode_callbacks = {MessageTypes.Logon.value: self.decode_logon,
                                 MessageTypes.Referential.value: self.decode_referential,
                                 MessageTypes.OrderBook.value: self.decode_order_book,
                                 MessageTypes.CreateOrder.value: self.decode_create_order}

    def decode_header(self, encoded_string):
        fmt = '>QB'
        header_size = struct.calcsize(fmt)
        message_length, message_type = struct.unpack_from(fmt, encoded_string)
        readable_bytes = len(encoded_string) - header_size
        if message_length > readable_bytes:
            raise NotEnoughBytes
        self.logger.debug('Message type [{}]'.format(message_type))
        self.logger.debug('Message length [{}]'.format(message_length))
        body = bytes(encoded_string[header_size: header_size + message_length])
        new_offset = header_size + message_length
        return message_type, body, new_offset

    def decode_buffer(self, encoded_string):
        decoded_objects = []
        try:
            while True:
                message_type, body, new_offset = self.decode_header(encoded_string)

                # TODO: Handle unsupported message type
                decoded_object = self.decode_callbacks[message_type](body)
                decoded_objects.append([message_type, decoded_object])

                encoded_string = encoded_string[new_offset:]
        except ValueError:
            pass
        except NotEnoughBytes:
            pass
        except struct.error:
            pass
        return decoded_objects, encoded_string

    def encode_referential(self, referential):
        referential_message = referential_pb2.Referential()
        instruments_size = len(referential)
        if instruments_size:
            for instrument_to_serialize in referential.get_instruments():
                instrument = referential_message.instruments.add()
                instrument.identifier = instrument_to_serialize.identifier
                instrument.name = instrument_to_serialize.name
                instrument.isin = instrument_to_serialize.isin
                instrument.currency_identifier = instrument_to_serialize.currency_identifier
        referential_bytes = referential_message.SerializeToString()

        self.logger.debug('Referential bytes [{}]'.format(referential_bytes))
        self.logger.debug('Referential bytes length [{}]'.format(len(referential_bytes)))
        encoded_referential = struct.pack('>QB', len(referential_bytes), MessageTypes.Referential.value)
        encoded_referential += referential_bytes
        return encoded_referential

    def decode_referential(self, encoded_referential):
        referential = Referential()
        referential_message = referential_pb2.Referential()
        referential_message.ParseFromString(encoded_referential)
        for decoded_instrument in referential_message.instruments:
            instrument = Instrument(identifier=decoded_instrument.identifier,
                                    name=decoded_instrument.name,
                                    isin=decoded_instrument.isin,
                                    currency_identifier=decoded_instrument.currency_identifier)
            referential.add_instrument(instrument)
        return referential

    def encode_order_book(self, order_book):
        order_book_message = orderbook_pb2.OrderBook()
        order_book_message.instrument_identifier = order_book.instrument_identifier
        order_book_message.statistics.last_price = order_book.last_price
        order_book_message.statistics.high_price = order_book.high_price
        order_book_message.statistics.low_price = order_book.low_price
        for order_to_serialize in order_book:
            order = order_book_message.orders.add()
            order.identifier = order_to_serialize.identifier
            order.way = order_to_serialize.way.way
            order.quantity = order_to_serialize.quantity
            order.canceled_quantity = order_to_serialize.canceled_quantity
            order.executed_quantity = order_to_serialize.executed_quantity
            order.price = order_to_serialize.price
            order.counterparty = order_to_serialize.counterparty
            order.timestamp = order_to_serialize.timestamp
        order_book_bytes = order_book_message.SerializeToString()
        encoded_order_book = struct.pack('>QB', len(order_book_bytes), MessageTypes.OrderBook.value)
        encoded_order_book += order_book_bytes
        return encoded_order_book

    def decode_order_book(self, encoded_order_book):
        order_book_message = orderbook_pb2.OrderBook()
        order_book_message.ParseFromString(encoded_order_book)
        order_book = OrderBook(order_book_message.instrument_identifier)
        order_book.last_price = order_book_message.statistics.last_price
        order_book.high_price = order_book_message.statistics.high_price
        order_book.low_price = order_book_message.statistics.low_price
        for decoded_order in order_book_message.orders:
            order = ServerOrder(identifier=decoded_order.identifier,
                                way=OrderWay(decoded_order.way),
                                instrument_identifier=order_book_message.instrument_identifier,
                                quantity=decoded_order.quantity,
                                canceled_quantity=decoded_order.canceled_quantity,
                                executed_quantity=decoded_order.executed_quantity,
                                price=decoded_order.price,
                                counterparty=decoded_order.counterparty,
                                timestamp=decoded_order.timestamp)
            order_book.add_order(order)
        self.logger.debug(order_book)
        return order_book

    def encode_create_order(self, create_order):
        create_order_message = createorder_pb2.CreateOrder()
        create_order_message.way = create_order.way.way
        create_order_message.quantity = create_order.quantity
        create_order_message.price = create_order.price
        create_order_message.instrument_identifier = create_order.instrument_identifier
        create_order_bytes = create_order_message.SerializeToString()
        encoded_create_order = struct.pack('>QB', len(create_order_bytes), MessageTypes.CreateOrder.value)
        encoded_create_order += create_order_bytes
        return encoded_create_order

    def decode_create_order(self, encoded_create_order):
        create_order_message = createorder_pb2.CreateOrder()
        create_order_message.ParseFromString(encoded_create_order)
        create_order = CreateOrder(way=OrderWay(create_order_message.way),
                                   quantity=create_order_message.quantity,
                                   price=create_order_message.price,
                                   instrument_identifier=create_order_message.instrument_identifier)
        return create_order

    def encode_logon(self, logon):
        logon_message = logon_pb2.Logon()
        logon_message.login = logon.login
        logon_message.password = logon.password
        logon_message_bytes = logon_message.SerializeToString()
        encoded_logon_message = struct.pack('>QB', len(logon_message_bytes), MessageTypes.Logon.value)
        encoded_logon_message += logon_message_bytes
        return encoded_logon_message

    def decode_logon(self, encoded_logon):
        logon_message = logon_pb2.Logon()
        logon_message.ParseFromString(encoded_logon)
        logon = Logon(login=logon_message.login, password=logon_message.password)
        return logon
