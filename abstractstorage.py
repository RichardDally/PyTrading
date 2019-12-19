from abc import ABCMeta, abstractmethod


class AbstractStorage:
    __metaclass__ = ABCMeta

    def initialize(self):
        pass

    def close(self):
        pass

    @abstractmethod
    def insert_user(self, login, password) -> None:
        pass

    @abstractmethod
    def is_valid_user(self, login, password) -> bool:
        pass

    @abstractmethod
    def book_deal(self, deal) -> None:
        pass
