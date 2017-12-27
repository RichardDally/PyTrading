from abc import ABCMeta, abstractmethod


class Storage:
    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def insert_user(self, login, password):
        pass

    @abstractmethod
    def is_valid_user(self, login, password):
        pass
