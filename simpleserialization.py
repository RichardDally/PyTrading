import logging
from serverorder import ServerOrder
from logon import Logon
from orderway import OrderWay
from createorder import CreateOrder
from orderbook import OrderBook
from instrument import Instrument
from referential import Referential
from staticdata import MessageTypes
from serialization import Serialization
from exceptions import NotEnoughBytes


class SimpleSerialization(Serialization):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.separator = '|'
        self.decode_callbacks = {MessageTypes.Logon.value: self.decode_logon,
                                 MessageTypes.Referential.value: self.decode_referential,
                                 MessageTypes.OrderBook.value: self.decode_order_book,
                                 MessageTypes.CreateOrder.value: self.decode_create_order}

    def decode_header(self, encoded_string):
        """ Decode header (total length + message type) """

        self.logger.debug('Encoded string [{}]'.format(encoded_string))

        if len(encoded_string) == 0:
            raise NotEnoughBytes

        decoded_buffer = encoded_string.decode('utf-8')
        try:
            message_length_separator_index = decoded_buffer.index(self.separator)
        except ValueError:
            self.logger.warning('No separator in decoded buffer [{}]'.format(decoded_buffer))
            raise NotEnoughBytes

        message_length = int(encoded_string[:message_length_separator_index])
        message = encoded_string[message_length_separator_index + 1:message_length + message_length_separator_index].decode('utf-8')
        self.logger.debug('Decode buffer, message type [{}]'.format(type(message)))

        self.logger.debug('Message length {}'.format(message_length))
        self.logger.debug('Message actual length [{}]'.format(len(message)))
        self.logger.debug('Message [{}]'.format(message))

        if len(message) != message_length - 1:
            self.logger.info('Message length does not match current message length')
            raise NotEnoughBytes

        message_type_separator_index = message.index(self.separator)
        message_type = int(message[:message_type_separator_index])
        body = message[message_type_separator_index + 1:]
        new_offset = message_length_separator_index + message_length

        return message_type, body, new_offset

    def decode_buffer(self, encoded_string):
        decoded_objects = []
        try:
            while True:
                message_type, body, new_offset = self.decode_header(encoded_string)
                try:
                    decoded_object = self.decode_callbacks[message_type](body)
                    decoded_objects.append([message_type, decoded_object])
                except KeyError:
                        self.logger.warning('Message type [{}] cannot be decoded'.format(message_type))
                encoded_string = encoded_string[new_offset:]
        except NotEnoughBytes:
            pass
        return decoded_objects, encoded_string

    def encode_referential(self, referential):
        message_type = str(MessageTypes.Referential.value)
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
        message_type = str(MessageTypes.OrderBook.value)

        statistics = '{1}{0}{2}{0}{3}{0}{4}'.format(
            self.separator,
            str(order_book.instrument_identifier),
            str(order_book.last_price),
            str(order_book.high_price),
            str(order_book.low_price))

        orders_string = ''
        orders = order_book.get_all_orders()
        for order in orders:
            orders_string += '{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}{0}{7}{0}{8}{0}'.format(
                self.separator,
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
            order_book.on_new_order(
                ServerOrder(instrument_identifier=instrument_identifier,
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
        message_type = MessageTypes.CreateOrder.value
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

    def encode_logon(self, logon):
        message_type = MessageTypes.Logon.value
        logon_string = "{0}{1}{0}{2}{0}{3}{0}".format(self.separator,
                                                      message_type,
                                                      logon.login,
                                                      logon.password)
        encoded_logon = str(len(logon_string)) + logon_string
        return bytearray(encoded_logon, 'utf-8')

    def decode_logon(self, encoded_logon):
        tokens = list(filter(None, encoded_logon.split(self.separator)))
        logon = Logon(login=tokens[0], password=tokens[1])
        return logon
