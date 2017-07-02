from way import Way
from staticdata import StaticData
import logging


class OrderBook:
    def __init__(self, instrument_identifier):
        self.logger = logging.getLogger(__name__)
        self.instrument_identifier = instrument_identifier
        self.asks = []
        self.bids = []

    # TODO: improve string formatting
    def __str__(self):
        string = '\n--- [{}] order book ---\n'.format(self.instrument_identifier)
        # TODO: fix it
        currency = 'FIXIT'
        #currency = StaticData.get_currency(self.instrument.currency_identifier)
        string += 'Last: {1} {0}\nHigh: {2} {0}\nLow: {3} {0}\n'.format(currency, self.last, self.high, self.low)
        if len(self.bids):
            string += 'Bid side ({}):\n'.format(len(self.bids))
            string += '\n'.join([str(o) for o in sorted(self.bids, key=lambda o: o.price, reverse = True)])
        if len(self.asks):
            if len(self.bids):
                string += '\n'
            string += 'Ask side ({}):\n'.format(len(self.asks))
            string += '\n'.join([str(o) for o in sorted(self.asks, key=lambda o: o.price)])
        return string

    def get_bids(self):
        return self.bids

    def get_asks(self):
        return self.asks

    def count_bids(self):
        return len(self.bids)

    def count_asks(self):
        return len(self.asks)

    def on_new_order(self, order):
        assert (order.instrument_identifier == self.instrument_identifier),\
            'Order instrument must match order book instrument'
        self.match_order(order)
        if order.get_remaining_quantity() > 0.0:
            self.logger.debug('Attacking order cannot be fully executed, adding [{}] to trading book'.format(order))
            self.add_order(order)
        else:
            self.logger.debug('Attacking order [{}] has been totally executed'.format(order))

    # TODO: finish implementation
    def on_new_deal(self, deal):
        self.last = deal.price
        if not self.high and not self.low:
            self.high = self.low = deal.price
        elif deal.price > self.high:
            self.high = deal.price
        elif deal.price < self.low:
            self.low = deal.price

    def add_order(self, order):
        if order.way == Way.BUY:
            self.bids.append(order)
        elif order.way == Way.SELL:
            self.asks.append(order)
        else:
            raise Exception('Way is invalid')

    def get_matching_orders(self, attacking_order):
        if attacking_order.way == Way.BUY:
            return sorted([x for x in self.asks if x.price <= attacking_order.price], key=lambda o: o.timestamp)
        elif attacking_order.way == Way.SELL:
            return sorted([x for x in self.bids if x.price >= attacking_order.price], key=lambda o: o.timestamp)
        raise Exception('Way is invalid')

    @staticmethod
    def is_attacked_order_full_executed(attacking_order, attacked_order):
        return attacking_order.get_remaining_quantity() >= attacked_order.get_remaining_quantity()

    def get_orders(self, way):
        if way == Way.BUY:
            return self.bids
        elif way == Way.SELL:
            return self.asks
        raise Exception('Way is invalid')

    def match_order(self, attacking_order):
        self.logger.debug('Find a matching order for [{}]'.format(attacking_order))
        matching_trading_book_orders = self.get_matching_orders(attacking_order)

        for attacked_order in matching_trading_book_orders:
            if self.is_attacked_order_full_executed(attacking_order, attacked_order):
                self.logger.debug('[{}] has been totally executed'.format(attacked_order))
                attacking_order.executed_quantity += attacked_order.get_remaining_quantity()
                attacked_order.executed_quantity += attacked_order.get_remaining_quantity()
                self.on_new_deal(attacked_order)
                self.get_orders(attacked_order.way).remove(attacked_order)
            else:
                self.logger.debug('[{}] has been partially executed'.format(attacked_order))
                attacking_order.executedquantity += attacking_order.get_remaining_quantity()
                attacked_order.executedquantity += attacking_order.get_remaining_quantity()
                self.on_new_deal(attacking_order)
            if attacking_order.get_remaining_quantity() == 0.0:
                break
