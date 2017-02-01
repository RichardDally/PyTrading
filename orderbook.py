from way import Way

class OrderBook:
    bids = None
    asks = None
    last = None
    high = None
    low = None

    def __init__(self):
        self.asks = []
        self.bids = []

    def __str__(self):
        stats = 'Last: {}\nHigh: {}\nLow: {}\n'.format(self.last, self.high, self.low)
        bidSide = '\n'.join([str(o) for o in sorted(self.bids, key=lambda o: o.price, reverse = True)])
        askSide = '\n'.join([str(o) for o in sorted(self.asks, key=lambda o: o.price)])
        return stats + 'Bid side:\n' + bidSide + '\nAsk side:\n' + askSide

    def count_buy_orders(self):
        return len(self.bids)

    def count_sell_orders(self):
        return len(self.asks)

    def on_new_order(self, order):
        self.match_order(order)
        if order.get_remaining_quantity() > 0.0:
            self.add_order(order)
        else:
            print('[Debug] entering order has been totally executed')

    # TODO: implement
    def on_new_deal(self, deal):
        self.last = deal.price
        if not self.high and not self.low:
            self.high = self.low = deal.price
        else:
            if deal.price > self.high:
                self.high = deal.price
            elif deal.price < self.low:
                self.low = deal.price

    def add_order(self, order):
        if order.way == Way.BUY:
            self.bids.append(order)
        elif order.way == Way.SELL:
            self.asks.append(order)

    def get_matching_orders(self, incomingOrder):
        if incomingOrder.way == Way.BUY:
            return sorted([x for x in self.asks if x.price <= incomingOrder.price], key=lambda o: o.timestamp)
        elif incomingOrder.way == Way.SELL:
            return sorted([x for x in self.bids if x.price >= incomingOrder.price], key=lambda o: o.timestamp)
        raise Exception('Way is not set')

    def match_order(self, incomingOrder):
        matchingTradingBookOrders = self.get_matching_orders(incomingOrder)

        for orderInTradingBook in matchingTradingBookOrders:
            # Full exec
            if incomingOrder.get_remaining_quantity() >= orderInTradingBook.get_remaining_quantity():
                print('[Debug] a trading book order has been totally executed ({})'.format(orderInTradingBook.get_remaining_quantity()))
                incomingOrder.executedquantity += orderInTradingBook.get_remaining_quantity()
                orderInTradingBook.executedquantity += orderInTradingBook.get_remaining_quantity()
                self.asks.remove(orderInTradingBook)
            else: # Partial exec
                print('[Debug] a trading book order has been partially executed ({})'.format(incomingOrder.get_remaining_quantity()))
                incomingOrder.executedquantity += incomingOrder.get_remaining_quantity()
                orderInTradingBook.executedquantity += incomingOrder.get_remaining_quantity()
                self.on_new_deal(incomingOrder)
            if incomingOrder.get_remaining_quantity() == 0.0:
                break
