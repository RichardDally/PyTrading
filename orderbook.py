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
        self.find_match(order)
        if order.get_remaining_quantity() > 0.0:
            self.add_order(order)
        else:
            print('[Debug] entering order has been totally executed')

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

    def find_match(self, order):
        if order.way == Way.BUY:
            matchingPrice = sorted([x for x in self.asks if x.price == order.price], key=lambda o: o.timestamp)
            for orderInTradingBook in matchingPrice:
                # Full exec                                                                                                                                                                                        
                if order.get_remaining_quantity() >= orderInTradingBook.get_remaining_quantity():
                    print('[Debug] a trading book order has been totally executed ({})'.format(orderInTradingBook.get_remaining_quantity()))
                    order.executedquantity += orderInTradingBook.get_remaining_quantity()
                    orderInTradingBook.executedquantity += orderInTradingBook.get_remaining_quantity()
                    self.asks.remove(orderInTradingBook)
                else: # Partial exec                                                                                                                                                                               
                    print('[Debug] a trading book order has been partially executed ({})'.format(order.get_remaining_quantity()))
                    order.executedquantity += order.get_remaining_quantity()
                    orderInTradingBook.executedquantity += order.get_remaining_quantity()
                    # TODO: create a deal                                                                                                                                                                          
                    self.on_new_deal(order)
                if order.get_remaining_quantity() == 0.0:
                    break
        elif order.way == Way.SELL:
            pass
            #matches = [x for x in self.bids if x.price == order.price]                                                                                                                                            
            #print(matches)