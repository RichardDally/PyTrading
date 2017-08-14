import struct
import traceback
import capnp
import referential_capnp
import orderbookfullsnapshot_capnp
from orderbook import OrderBook
from instrument import Instrument
from referential import Referential
from staticdata import StaticData
from staticdata import MessageTypes
from serialization import Serialization


class CapnpSerialization(Serialization):
    @staticmethod
    def decode_buffer(buffer, handle_callbacks):
        decode_callbacks = {MessageTypes.Referential: CapnpSerialization.decode_referential,
                            MessageTypes.OrderBook: CapnpSerialization.decode_order_book}
        decoded_messages_count = 0
        header_size = 9
        try:
            while len(buffer) > header_size:
                message_length, message_type = struct.unpack_from('>Qc', buffer)
                readable_bytes = len(buffer) - header_size
                # TODO: bring back the logs
                #print('Message length [{}]'.format(message_length))
                #print('Message type [{}]'.format(message_type))
                if message_length > readable_bytes:
                    #print('Not enough bytes ({}) to decode current message ({})'.format(readable_bytes, message_length))
                    break
                encoded_message = buffer[header_size: header_size + message_length]

                # TODO: Handle unsupported message type
                decoded_object = decode_callbacks[message_type](encoded_message)
                handle_callbacks[message_type](decoded_object)

                buffer = buffer[header_size + message_length:]
                decoded_messages_count += 1
        except Exception as exception:
            print('decode_buffer: {}'.format(exception))
            print(traceback.print_exc())
        return decoded_messages_count, buffer

    @staticmethod
    def encode_referential(referential):
        referential_message = referential_capnp.Referential.new_message()
        instruments_size = len(referential)
        if instruments_size:
            instrument_list = referential_message.init('instruments', instruments_size)
            for index, instrument in enumerate(referential.get_instruments()):
                instrument_list[index].identifier = instrument.identifier
                instrument_list[index].name = instrument.name
                instrument_list[index].isin = instrument.isin
                instrument_list[index].currencyIdentifier = instrument.currency_identifier
        referential_bytes = referential_message.to_bytes()
        encoded_referential = struct.pack('>Qc', len(referential_bytes), MessageTypes.Referential) + referential_bytes
        return encoded_referential


    @staticmethod
    def decode_referential(encoded_referential):
        referential = Referential()
        referential_message = referential_capnp.Referential.from_bytes(encoded_referential)
        for decodedInstrument in referential_message.instruments:
            instrument = Instrument(identifier=decodedInstrument.identifier,
                                    name=decodedInstrument.name,
                                    isin=decodedInstrument.isin,
                                    currency_identifier=decodedInstrument.currencyIdentifier)
            referential.add_instrument(instrument)
        return referential

    @staticmethod
    def encode_orders(order_book_message, order_book, side):
        orders_count = eval('order_book.count_{}()'.format(side))
        if orders_count:
            orders = order_book_message.init(side, orders_count)
            for index, order in enumerate(eval('order_book.get_{}()'.format(side))):
                orders[index].order_identifier = order.identifier
                orders[index].way = order.way
                orders[index].quantity = order.quantity
                orders[index].price = order.price
                orders[index].timestamp = order.timestamp

    @staticmethod
    def encode_order_book(order_book):
        order_book_message = orderbookfullsnapshot_capnp.OrderBookFullSnapshot.new_message()
        order_book_message.instrumentIdentifier = order_book.instrument_identifier
        order_book_message.statistics.lastPrice = order_book.last
        order_book_message.statistics.highPrice = order_book.high
        order_book_message.statistics.lowPrice = order_book.low
        CapnpSerialization.encode_orders(order_book_message, order_book, 'bids')
        CapnpSerialization.encode_orders(order_book_message, order_book, 'asks')

        order_book_bytes = order_book_message.to_bytes()
        encoded_order_book = struct.pack('>Qc', len(order_book_bytes), MessageTypes.OrderBook) + order_book_bytes
        return encoded_order_book

    @staticmethod
    def decode_orders(decoded_order_book, order_book, side):
        for decoded_order in eval('decoded_order_book.{}'.format(side)):
            order = Order(identifier=decoded_order.order_identifier,
                          way=decoded_order.way,
                          instrument=StaticData.get_instrument(decoded_order.instrument_identifier),
                          quantity=decoded_order.quantity,
                          price=decoded_order.price,
                          counterparty=decoded_order.counterparty,
                          timestamp=decoded_order.timestamp)
            eval('order_book.{}.append(order)'.format(side))

    @staticmethod
    def decode_order_book(encoded_order_book):
        decoded_order_book = orderbookfullsnapshot_capnp.OrderBookFullSnapshot.from_bytes(encoded_order_book)
        order_book = OrderBook(StaticData.get_instrument(decoded_order_book.instrumentIdentifier))
        order_book.last = decoded_order_book.statistics.lastPrice
        order_book.high = decoded_order_book.statistics.highPrice
        order_book.low = decoded_order_book.statistics.lowPrice
        CapnpSerialization.decode_orders(decoded_order_book, order_book, 'bids')
        CapnpSerialization.decode_orders(decoded_order_book, order_book, 'asks')
        #print(order_book)
        return order_book
