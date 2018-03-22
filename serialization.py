from abc import ABCMeta, abstractmethod


class Serialization:
    __metaclass__ = ABCMeta

    @abstractmethod
    def decode_header(self, encoded_string):
        pass

    @abstractmethod
    def decode_buffer(self, encoded_string):
        pass

    @abstractmethod
    def encode_referential(self, referential):
        pass

    @abstractmethod
    def decode_referential(self, encoded_referential):
        pass

    @abstractmethod
    def encode_order_book(self, order_book):
        pass

    @abstractmethod
    def decode_order_book(self, encoded_order_book):
        pass

    @abstractmethod
    def encode_create_order(self, create_order):
        pass

    @abstractmethod
    def decode_create_order(self, encoded_create_order):
        pass

    @abstractmethod
    def encode_logon(self, logon):
        pass

    @abstractmethod
    def decode_logon(self, encoded_logon):
        pass
