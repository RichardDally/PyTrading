from way import Way
import logging

class OrderBook:
    logger = logging.getLogger(__name__)
    bids = None
    asks = None
    last = None
    high = None
    low = None
    instrument = None

    def __init__(self, instrument):
        self.instrument = instrument
        self.asks = []
        self.bids = []

    # TODO: improve string formating
    def __str__(self):
        string = '\n--- [{}] order book ---\n'.format(self.instrument)
        string += 'Last: {1} {0}\nHigh: {2} {0}\nLow: {3} {0}\n'.format(self.instrument.currency, self.last, self.high, self.low)
        if len(self.bids):
            string += 'Bid side ({}):\n'.format(len(self.bids))
            string += '\n'.join([str(o) for o in sorted(self.bids, key=lambda o: o.price, reverse = True)])
        if len(self.asks):
            if len(self.bids):
                string += '\n'
            string += 'Ask side ({}):\n'.format(len(self.asks))
            string += '\n'.join([str(o) for o in sorted(self.asks, key=lambda o: o.price)])
        return string

    def count_buy_orders(self):
        return len(self.bids)

    def count_sell_orders(self):
        return len(self.asks)

    def on_new_order(self, order):
        assert (order.instrument == self.instrument), 'Order instrument must match order book instrument'
        self.match_order(order)
        if order.get_remaining_quantity() > 0.0:
            self.logger.debug('Attacking order cannot be fully executed, adding [{}] to trading book'.format(order))
            self.add_order(order)
        else:
            self.logger.debug('Attacking order [{}] has been totally executed'.format(order))

    # TODO: implement
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

    def get_matching_orders(self, attackingOrder):
        if attackingOrder.way == Way.BUY:
            return sorted([x for x in self.asks if x.price <= attackingOrder.price], key=lambda o: o.timestamp)
        elif attackingOrder.way == Way.SELL:
            return sorted([x for x in self.bids if x.price >= attackingOrder.price], key=lambda o: o.timestamp)
        raise Exception('Way is invalid')

    def is_attacked_order_full_executed(self, attackingOrder, attackedOrder):
        return attackingOrder.get_remaining_quantity() >= attackedOrder.get_remaining_quantity()

    def get_orders(self, way):
        if way == Way.BUY:
            return self.bids
        elif way == Way.SELL:
            return self.asks
        raise Exception('Way is invalid')

    def match_order(self, attackingOrder):
        self.logger.debug('Find a matching order for [{}]'.format(attackingOrder))
        matchingTradingBookOrders = self.get_matching_orders(attackingOrder)

        for attackedOrder in matchingTradingBookOrders:
            if self.is_attacked_order_full_executed(attackingOrder, attackedOrder):
                self.logger.debug('[{}] has been totally executed'.format(attackedOrder))
                attackingOrder.executedquantity += attackedOrder.get_remaining_quantity()
                attackedOrder.executedquantity += attackedOrder.get_remaining_quantity()
                self.on_new_deal(attackedOrder)
                self.get_orders(attackedOrder.way).remove(attackedOrder)
            else: # Partial execution
                self.logger.debug('[{}] has been partially executed ({})'.format(attackedOrder))
                attackingOrder.executedquantity += attackingOrder.get_remaining_quantity()
                attackedOrder.executedquantity += attackingOrder.get_remaining_quantity()
                self.on_new_deal(attackingOrder)
            if attackingOrder.get_remaining_quantity() == 0.0:
                break
