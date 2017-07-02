import capnp
import referential_capnp
import orderbookfullsnapshot_capnp
from orderbook import OrderBook
from instrument import Instrument
from referential import Referential
from staticdata import StaticData
from serialization import Serialization

# TODO: fix Cap n Proto implementation
class CapnpSerialization(Serialization):
    @staticmethod
    def decode_buffer(buffer, decode_callbacks):
        decoded_messages = 0
        header_size = 9
        while len(buffer) > header_size:
            message_length, message_type = struct.unpack_from('>Qc', buffer)
            readable_bytes = len(self.buffer) - header_size
            # TODO: bring back the logs
            #self.logger.debug('Message length [{}]'.format(message_length))
            #self.logger.debug('Message type [{}]'.format(message_type))
            if message_length > readable_bytes:
                #self.logger.debug('Not enough bytes to decode current message')
                break
            # TODO: Handle unsupported message type
            self.decode_mapping[message_type](self.buffer[header_size: header_size + message_length])
            self.logger.debug('Buffer length before [{}]'.format(len(self.buffer)))
            self.buffer = self.buffer[header_size + message_length:]
            self.logger.debug('Buffer length after [{}]'.format(len(self.buffer)))
            decoded_messages += decoded_messages + 1
        return decoded_messages

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
                instrument_list[index].currency_identifier = instrument.currency_identifier
        return referential_message.to_bytes()

    @staticmethod
    def decode_referential(encoded_referential):
        referential = Referential()
        referential_message = referential_capnp.Referential.from_bytes(encoded_referential)
        for decodedInstrument in referential_message.instruments:
            instrument = Instrument(identifier=decodedInstrument.identifier,
                                    name=decodedInstrument.name,
                                    isin=decodedInstrument.isin,
                                    currency_identifier=decodedInstrument.currency_identifier)
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
        order_book_message.instrument_identifier = order_book.instrument.identifier
        order_book_message.statistics.lastPrice = order_book.last
        order_book_message.statistics.highPrice = order_book.high
        order_book_message.statistics.lowPrice = order_book.low
        __class__.encode_orders(order_book_message, order_book, 'bids')
        __class__.encode_orders(order_book_message, order_book, 'asks')
        return order_book_message

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
    def decode_order_book_snapshot(order_book_snapshot):
        decoded_order_book = orderbookfullsnapshot_capnp.OrderBookFullSnapshot.from_bytes(order_book_snapshot)
        order_book = OrderBook(StaticData.get_instrument(decoded_order_book.instrument_identifier))
        order_book.last = decoded_order_book.statistics.lastPrice
        order_book.high = decoded_order_book.statistics.highPrice
        order_book.low = decoded_order_book.statistics.lowPrice
        Serialization.decode_orders(decoded_order_book, order_book, 'bids')
        Serialization.decode_orders(decoded_order_book, order_book, 'asks')
        return order_book
