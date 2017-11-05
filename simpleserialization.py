from order import Order
from orderway import OrderWay
from createorder import CreateOrder
from orderbook import OrderBook
from instrument import Instrument
from referential import Referential
from staticdata import MessageTypes
from serialization import Serialization, NotEnoughBytes


class SimpleSerialization(Serialization):
    def __init__(self):
        self.separator = '|'
        self.decode_callbacks = {MessageTypes.Referential: self.decode_referential,
                                 MessageTypes.OrderBook: self.decode_order_book,
                                 MessageTypes.CreateOrder: self.decode_create_order}

    def decode_header(self, buffer):
        """ Decode header (total length + message type)"""
        # print('buffer [{}]'.format(buffer))
        message_length_separator_index = buffer.decode('utf-8').index(self.separator)
        message_length = int(buffer[:message_length_separator_index])
        message = buffer[message_length_separator_index + 1:message_length + message_length_separator_index].decode('utf-8')
        # print('decode buffer, message type [{}]'.format(type(message)))

        # print('Message length {}'.format(message_length))
        # print('Message actual length [{}]'.format(len(message)))
        # print('Message [{}]'.format(message))

        if len(message) != message_length - 1:
            print('Message length does not match current message length')
            raise NotEnoughBytes

        message_type_separator_index = message.index(self.separator)
        message_type = int(message[:message_type_separator_index])
        body = message[message_type_separator_index + 1:]
        new_offset = message_length_separator_index + message_length

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

        return decoded_messages_count, buffer

    def encode_referential(self, referential):
        message_type = str(MessageTypes.Referential)
        instruments = ''
        for instrument in referential.get_instruments():
            instruments += str(instrument.identifier) + self.separator
            instruments += instrument.name + self.separator
            instruments += instrument.isin + self.separator
            instruments += str(instrument.currency_identifier) + self.separator
        referential_string = self.separator + message_type + self.separator + instruments
        encoded_referential = str(len(referential_string)) + referential_string
        return bytearray(encoded_referential, 'utf-8')

    def decode_referential(self, encoded_referential):
        referential = Referential()
        tokens = list(filter(None, encoded_referential.split(self.separator)))
        for x in range(0, len(tokens), 4):
            referential.add_instrument(Instrument(identifier=int(tokens[x]),
                                                  name=tokens[x + 1],
                                                  isin=tokens[x + 2],
                                                  currency_identifier=int(tokens[x + 3])))

        return referential

    def encode_order_book(self, order_book):
        message_type = str(MessageTypes.OrderBook)

        # TODO: replace pipe by self.separator
        statistics = '{}|{}|{}|{}'.format(
            str(order_book.instrument_identifier),
            str(order_book.last_price),
            str(order_book.high_price),
            str(order_book.low_price))

        orders_string = ''
        orders = order_book.get_all_orders()
        for order in orders:
            # TODO: replace pipe by self.separator
            orders_string += '{}|{}|{}|{}|{}|{}|{}|{}|'.format(
                str(order.identifier),
                str(order.way.way),
                str(order.quantity),
                str(order.canceled_quantity),
                str(order.executed_quantity),
                str(order.price),
                str(order.counterparty),
                str(order.timestamp)
            )

        order_book_string = self.separator + message_type + self.separator + statistics + self.separator + orders_string
        encoded_order_book = str(len(order_book_string)) + order_book_string

        return bytearray(encoded_order_book, 'utf-8')

    def decode_order_book(self, encoded_order_book):
        tokens = list(filter(None, encoded_order_book.split(self.separator)))

        instrument_identifier = int(tokens[0])
        order_book = OrderBook(instrument_identifier)
        order_book.last_price = float(tokens[1])
        order_book.high_price = float(tokens[2])
        order_book.low_price = float(tokens[3])

        order_tokens = tokens[4:]
        for x in range(0, len(order_tokens), 8):
            order_book.add_order(
                Order(instrument_identifier=instrument_identifier,
                      identifier=int(order_tokens[x]),
                      way=OrderWay(int(order_tokens[x + 1])),
                      quantity=float(order_tokens[x + 2]),
                      canceled_quantity=float(order_tokens[x + 3]),
                      executed_quantity=float(order_tokens[x + 4]),
                      price=float(order_tokens[x + 5]),
                      counterparty=order_tokens[x + 6],
                      timestamp=order_tokens[x + 7])
            )

        return order_book

    def encode_create_order(self, create_order):
        message_type = MessageTypes.CreateOrder
        create_order_string = "{0}{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}"\
            .format(self.separator,
                    str(message_type),
                    str(create_order.way.way),
                    str(create_order.price),
                    str(create_order.quantity),
                    str(create_order.instrument_identifier))
        encoded_create_order = str(len(create_order_string)) + create_order_string
        return bytearray(encoded_create_order, 'utf-8')

    def decode_create_order(self, encoded_create_order):
        tokens = list(filter(None, encoded_create_order.split(self.separator)))
        create_order = CreateOrder(way=OrderWay(int(tokens[0])),
                                   price=float(tokens[1]),
                                   quantity=float(tokens[2]),
                                   instrument_identifier=int(tokens[3]))
        return create_order
