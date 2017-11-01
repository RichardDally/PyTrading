import struct
import orderbook_pb2
import referential_pb2
from order import Order
from orderbook import OrderBook
from instrument import Instrument
from referential import Referential
from staticdata import MessageTypes
from serialization import Serialization, NotEnoughBytes


class ProtobufSerialization(Serialization):
    def __init__(self):
        self.decode_callbacks = {MessageTypes.Referential: self.decode_referential,
                                 MessageTypes.OrderBook: self.decode_order_book}

    def decode_header(self, buffer):
        fmt = '>QB'
        header_size = struct.calcsize(fmt)
        message_length, message_type = struct.unpack_from(fmt, buffer)
        readable_bytes = len(buffer) - header_size
        if message_length > readable_bytes:
            raise NotEnoughBytes
        #print('Message type [{}]'.format(message_type))
        #print('Message length [{}]'.format(message_length))
        body = bytes(buffer[header_size: header_size + message_length])
        new_offset = header_size + message_length
        return message_type, body, new_offset

    def decode_buffer(self, buffer, handle_callbacks):
        decoded_messages_count = 0
        try:
            while True:
                message_type, body, new_offset = self.decode_header(buffer)

                # TODO: Handle unsupported message type
                decoded_object = self.decode_callbacks[message_type](body)
                handle_callbacks[message_type](decoded_object)

                buffer = buffer[new_offset:]
                decoded_messages_count += 1
        except ValueError:
            pass
        except NotEnoughBytes:
            pass
        except struct.error:
            pass
        return decoded_messages_count, buffer

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

        #print('Referential bytes [{}]'.format(referential_bytes))
        #print('Referential bytes length [{}]'.format(len(referential_bytes)))
        encoded_referential = struct.pack('>QB', len(referential_bytes), MessageTypes.Referential) + referential_bytes
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
            order.way = order_to_serialize.way
            order.quantity = order_to_serialize.quantity
            order.canceled_quantity = order_to_serialize.canceled_quantity
            order.executed_quantity = order_to_serialize.executed_quantity
            order.price = order_to_serialize.price
            order.counterparty = order_to_serialize.counterparty
            order.timestamp = order_to_serialize.timestamp
        order_book_bytes = order_book_message.SerializeToString()
        encoded_order_book = struct.pack('>QB', len(order_book_bytes), MessageTypes.OrderBook) + order_book_bytes
        return encoded_order_book

    def decode_order_book(self, encoded_order_book):
        order_book_message = orderbook_pb2.OrderBook()
        order_book_message.ParseFromString(encoded_order_book)
        order_book = OrderBook(order_book_message.instrument_identifier)
        order_book.last_price = order_book_message.statistics.last_price
        order_book.high_price = order_book_message.statistics.high_price
        order_book.low_price = order_book_message.statistics.low_price
        for decoded_order in order_book_message.orders:
            order = Order(identifier=decoded_order.identifier,
                          way=decoded_order.way,
                          instrument_identifier=order_book_message.instrument_identifier,
                          quantity=decoded_order.quantity,
                          canceled_quantity=decoded_order.canceled_quantity,
                          executed_quantity=decoded_order.executed_quantity,
                          price=decoded_order.price,
                          counterparty=decoded_order.counterparty,
                          timestamp=decoded_order.timestamp)
            order_book.add_order(order)
        #print(order_book)
        return order_book
