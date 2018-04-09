import logging
from orderway import Buy, Sell
from exceptions import InvalidWay


class OrderBook:
    def __init__(self, instrument_identifier):
        self.logger = logging.getLogger(__name__)
        self.instrument_identifier = instrument_identifier
        self.asks = []
        self.bids = []
        self.last_price = 0.0
        self.high_price = 0.0
        self.low_price = 0.0

    def __iter__(self):
        for order in self.asks:
            yield order
        for order in self.bids:
            yield order

    # TODO: improve string formatting
    def __str__(self):
        string = '\n--- [{}] order book ---\n'.format(self.instrument_identifier)
        string += 'Last: {} \nHigh: {} \nLow: {} \n'.format(self.last_price, self.high_price, self.low_price)
        if len(self.bids):
            string += 'Bid side ({}):\n'.format(len(self.bids))
            string += '\n'.join([str(o) for o in sorted(self.bids, key=lambda o: o.price, reverse=True)])
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
        """ Count buy orders """
        return len(self.bids)

    def count_asks(self):
        """ Count sell orders """
        return len(self.asks)

    def on_new_order(self, order):
        if order.instrument_identifier != self.instrument_identifier:
            raise Exception('Order instrument must match order book instrument')

        quantity_before_execution = order.get_remaining_quantity()
        self.match_order(order)
        if quantity_before_execution == order.get_remaining_quantity():
            self.logger.info('Attacking order is unmatched, adding [{}] to trading book'.format(order))
            self.add_order(order)
        elif order.get_remaining_quantity() > 0.0:
            self.logger.info('Attacking order cannot be fully executed, adding [{}] to trading book'.format(order))
            self.add_order(order)
        else:
            self.logger.info('Attacking order [{}] has been totally executed'.format(order))

    # TODO: create and store a deal (not just updating orderbook stats)
    def on_new_deal(self, order):
        self.last_price = order.price
        if not self.high_price and not self.low_price:
            self.high_price = self.low_price = order.price
        elif order.price > self.high_price:
            self.high_price = order.price
        elif order.price < self.low_price:
            self.low_price = order.price

    def add_order(self, order):
        """ Do not call add_order directly, use on_new_order instead """
        if order.way == Buy():
            self.bids.append(order)
        elif order.way == Sell():
            self.asks.append(order)
        else:
            raise InvalidWay(order.way)

    def get_matching_orders(self, attacking_order):
        if attacking_order.way == Buy():
            return sorted([s for s in self.asks if s.counterparty != attacking_order.counterparty and s.price <= attacking_order.price], key=lambda o: o.timestamp)
        if attacking_order.way == Sell():
            return sorted([b for b in self.bids if b.counterparty != attacking_order.counterparty and b.price >= attacking_order.price], key=lambda o: o.timestamp)
        raise InvalidWay(attacking_order.way)

    @staticmethod
    def is_attacked_order_full_executed(attacking_order, attacked_order):
        return attacking_order.get_remaining_quantity() >= attacked_order.get_remaining_quantity()

    def get_all_orders(self):
        return self.bids + self.asks

    def get_orders(self, way):
        if way == Buy():
            return self.bids
        if way == Sell():
            return self.asks
        raise InvalidWay

    def match_order(self, attacking_order):
        self.logger.info('Find a matching order for [{}]'.format(attacking_order))
        matching_trading_book_orders = self.get_matching_orders(attacking_order)

        for attacked_order in matching_trading_book_orders:
            if self.is_attacked_order_full_executed(attacking_order, attacked_order):
                attacking_order.executed_quantity += attacked_order.get_remaining_quantity()
                attacked_order.executed_quantity += attacked_order.get_remaining_quantity()
                self.on_new_deal(attacked_order)
                self.get_orders(attacked_order.way).remove(attacked_order)
            else:
                attacking_order.executedquantity += attacking_order.get_remaining_quantity()
                attacked_order.executedquantity += attacking_order.get_remaining_quantity()
                self.on_new_deal(attacking_order)
            if attacking_order.get_remaining_quantity() == 0.0:
                break
