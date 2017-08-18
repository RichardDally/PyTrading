class NotEnoughBytes(BaseException):
    """ Unable to decode message, available bytes are less than required """


class Serialization:
    @staticmethod
    def decode_header(buffer):
        pass

    @staticmethod
    def decode_buffer(buffer, handle_callbacks):
        pass

    @staticmethod
    def encode_referential(referential):
        pass

    @staticmethod
    def decode_referential(encoded_referential):
        pass

    @staticmethod
    def encode_order_book(order_book):
        pass

    @staticmethod
    def decode_order_book(encoded_order_book):
        pass
