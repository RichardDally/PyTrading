from loguru import logger
from pytrading import InvalidWay
from pytrading import Buy, Sell
from pytrading import OrderBookChanges
from pytrading import ServerOrder
from pytrading import ServerDeal


class OrderBook:
    def __init__(self, instrument_identifier: int):
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

    def __str__(self):
        """
        Use pretty function to have a detailed order book overview
        """
        return f"Instrument id [{self.instrument_identifier}] " \
               f"orders count [{self.count_all_orders()}] " \
               f"last [{self.last_price}] " \
               f"high [{self.high_price}] " \
               f"low [{self.low_price}]"

    def pretty(self, remaining_quantity: bool) -> str:
        string = f"\n--- [{self.instrument_identifier}] order book ---\n"
        string += f"Last: {self.last_price} \nHigh: {self.high_price} \nLow: {self.low_price} \n"
        if len(self.bids):
            string += f"Bid side ({self.count_bids()}):\n"
            string += "\n".join([str(order) for order in sorted(self.bids, key=lambda order: order.price, reverse=True)])
        if len(self.asks):
            if len(self.bids):
                string += "\n"
            string += f"Ask side ({self.count_asks()}):\n"
            string += "\n".join([order.pretty(remaining_quantity) for order in sorted(self.asks, key=lambda order: order.price)])
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

    def count_all_orders(self):
        return self.count_bids() + self.count_asks()

    def on_new_order(self, order: ServerOrder, apply_changes=False) -> OrderBookChanges:
        """
        Entry point to process a new order in order book
        apply_changes indicates either order book changes are applied directly at the end (testing purpose)
        """
        if order.instrument_identifier != self.instrument_identifier:
            raise Exception("[LOGIC FAILURE] Order instrument must match order book instrument")

        quantity_before_execution = order.get_remaining_quantity()
        changes = self.match_order(order)
        # Case 1: unmatched
        if quantity_before_execution == order.get_remaining_quantity():
            logger.debug(f"Attacking order is unmatched, adding [{order}] to trading book")
            changes.order_to_add.append(order)
        # Case 2: partially executed (existing order(s) have been executed)
        elif order.get_remaining_quantity() > 0.0:
            logger.debug(f"Attacking order cannot be fully executed, adding [{order}] to trading book")
            changes.order_to_add.append(order)
        # Case 3: order has been fully executed
        else:
            logger.debug(f"Attacking order [{order}] has been totally executed")

        if apply_changes:
            self.apply_order_book_changes(changes)

        return changes

    def apply_order_book_changes(self, order_book_changes: OrderBookChanges):
        """
        TODO: deal processing (order_book_changes.deal_to_add)
        """
        for order in order_book_changes.order_to_add:
            self.add_order(order)
        for order_to_remove in order_book_changes.order_to_remove:
            # TODO: improve removal ?
            self.get_orders(order_to_remove.way).remove(order_to_remove)

    def update_statistics(self, last_executed_order):
        self.last_price = last_executed_order.price
        if not self.high_price and not self.low_price:
            self.high_price = self.low_price = last_executed_order.price
        elif last_executed_order.price > self.high_price:
            self.high_price = last_executed_order.price
        elif last_executed_order.price < self.low_price:
            self.low_price = last_executed_order.price

    def add_order(self, order):
        """
        Do not call add_order directly, use on_new_order instead on server side
        """
        if order.way == Buy():
            self.bids.append(order)
        elif order.way == Sell():
            self.asks.append(order)
        else:
            raise InvalidWay(order.way)

    def get_matching_orders(self, attacking_order):
        """
        TODO: tweak matching rules to increase flexibility
        """
        if attacking_order.way == Buy():
            return sorted([s for s in self.asks if s.counterparty != attacking_order.counterparty and s.price <= attacking_order.price],
                          key=lambda o: o.timestamp)
        if attacking_order.way == Sell():
            return sorted([b for b in self.bids if b.counterparty != attacking_order.counterparty and b.price >= attacking_order.price],
                          key=lambda o: o.timestamp)
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

    def match_order(self, attacking_order) -> OrderBookChanges:
        logger.debug(f"Find a matching order for [{attacking_order}]")
        matching_trading_book_orders = self.get_matching_orders(attacking_order)
        return self.update_matched_orders(attacking_order, matching_trading_book_orders)

    def update_matched_orders(self, attacking_order: ServerOrder, matching_orders) -> OrderBookChanges:
        """
        Iterate and update attacked orders, create deals upon total and partial executions
        """
        changes = OrderBookChanges()

        for attacked_order in matching_orders:
            if self.is_attacked_order_full_executed(attacking_order, attacked_order):
                executed_quantity = attacked_order.get_remaining_quantity()
                attacking_order.executed_quantity += executed_quantity
                attacked_order.executed_quantity += executed_quantity
                self.update_statistics(last_executed_order=attacked_order)
                logger.debug(f"Attacker [{attacking_order.counterparty}]")
                logger.debug(f"Attacked [{attacked_order.counterparty}]")
                # Create deal
                deal = ServerDeal(attacking_order, attacked_order, executed_quantity)
                changes.deals_to_add.append(deal)
                # Remove executed order
                changes.order_to_remove.append(attacked_order)
            else:
                executed_quantity = attacking_order.get_remaining_quantity()
                attacking_order.executed_quantity += executed_quantity
                attacked_order.executed_quantity += executed_quantity
                self.update_statistics(last_executed_order=attacking_order)
                # Create a deal
                deal = ServerDeal(attacking_order, attacked_order, executed_quantity)
                changes.deals_to_add.append(attacking_order)
            if attacking_order.get_remaining_quantity() == 0.0:
                break

        return changes
