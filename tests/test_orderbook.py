from pytrading import Buy, Sell
from pytrading import ServerOrder
from pytrading import OrderBook
from pytrading import Instrument


class TestOrderBook:
    def setup_method(self, _):
        self.instrument = Instrument(identifier=0, name='Carrefour', isin='FR0000120172', currency_identifier=0)
        self.book = OrderBook(self.instrument.identifier)

    def test_count_bids(self):
        buy_order = ServerOrder(Buy(), self.instrument.identifier, 50, 42.0, 'Trader1')
        assert self.book.count_bids() == 0
        self.book.on_new_order(buy_order, apply_changes=True)
        assert self.book.count_bids() == 1

    def test_count_asks(self):
        sell_order = ServerOrder(Sell(), self.instrument.identifier, 50, 42.0, 'Trader1')
        assert self.book.count_asks() == 0
        self.book.on_new_order(sell_order, apply_changes=True)
        assert self.book.count_asks() == 1

    def test_get_bids(self):
        bids = self.book.get_bids()
        assert len(bids) == 0

    def test_get_asks(self):
        asks = self.book.get_asks()
        assert len(asks) == 0

    def test_self_execution(self):
        """
        Ensure you cannot trade against yourself
        """
        orders = [ServerOrder(Buy(), self.instrument.identifier, 50, 40.0, 'Trader1'),
                  ServerOrder(Sell(), self.instrument.identifier, 50, 40.0, 'Trader1')]
        for order in orders:
            self.book.on_new_order(order, apply_changes=True)
        assert self.book.count_bids() == 1
        assert self.book.count_asks() == 1

    def test_two_orders_no_match(self):
        """
        Two orders not matching (different price)
        """
        buy_order = ServerOrder(Buy(), self.instrument.identifier, 50, 40.0, 'Trader1')
        sell_order = ServerOrder(Sell(), self.instrument.identifier, 50, 42.0, 'Trader2')
        self.book.on_new_order(buy_order, apply_changes=True)
        self.book.on_new_order(sell_order, apply_changes=True)
        assert self.book.count_bids() == 1
        assert self.book.count_asks() == 1

    def test_four_stacked_orders_no_match(self):
        orders = [ServerOrder(Buy(), self.instrument.identifier, 50, 40.0, 'Trader1'),
                  ServerOrder(Buy(), self.instrument.identifier, 50, 40.0, 'Trader1'),
                  ServerOrder(Sell(), self.instrument.identifier, 50, 42.0, 'Trader2'),
                  ServerOrder(Sell(), self.instrument.identifier, 50, 42.0, 'Trader2')]
        for order in orders:
            self.book.on_new_order(order, apply_changes=True)
        assert self.book.count_bids() == 2
        assert self.book.count_asks() == 2

    def validate_one_matching(self, attacking_order, attacked_order):
        self.book.on_new_order(attacked_order, apply_changes=True)
        matching_orders = self.book.get_matching_orders(attacking_order)
        assert len(matching_orders) == 1
        assert matching_orders[0].__dict__ == attacked_order.__dict__

    def test_buy_price_greater_than_sell(self):
        attacking_order = ServerOrder(Buy(), self.instrument.identifier, 10, 40.0, 'Trader1')
        attacked_order = ServerOrder(Sell(), self.instrument.identifier, 10, 38.0, 'Trader2')
        self.validate_one_matching(attacking_order, attacked_order)
        assert attacking_order.get_remaining_quantity() == 10
        assert attacked_order.get_remaining_quantity() == 10

    def test_buy_price_equal_to_sell(self):
        attacking_order = ServerOrder(Buy(), self.instrument.identifier, 10, 40.0, 'Trader1')
        attacked_order = ServerOrder(Sell(), self.instrument.identifier, 10, 40.0, 'Trader2')
        self.book.on_new_order(attacked_order, apply_changes=True)
        self.book.on_new_order(attacking_order, apply_changes=True)
        assert attacking_order.get_remaining_quantity() == 0
        assert attacked_order.get_remaining_quantity() == 0

    def test_sell_price_greater_than_buy(self):
        attacking_order = ServerOrder(Sell(), self.instrument.identifier, 10, 40.0, 'Trader1')
        attacked_order = ServerOrder(Buy(), self.instrument.identifier, 10, 42.0, 'Trader2')
        self.validate_one_matching(attacking_order, attacked_order)

    def test_sell_price_equal_to_buy(self):
        attacking_order = ServerOrder(Sell(), self.instrument.identifier, 10, 40.0, 'Trader1')
        attacked_order = ServerOrder(Buy(), self.instrument.identifier, 10, 40.0, 'Trader2')
        self.validate_one_matching(attacking_order, attacked_order)

    def test_fifo_matching_orders(self):
        """
        Ensure FIFO matching is enforced
        """
        orders = [ServerOrder(Buy(), self.instrument.identifier, 50, 40.0, 'Trader1', timestamp=1),
                  ServerOrder(Buy(), self.instrument.identifier, 50, 40.0, 'Trader2', timestamp=2),
                  ServerOrder(Sell(), self.instrument.identifier, 50, 40.0, 'Trader3', timestamp=3)]
        for order in orders:
            self.book.on_new_order(order, apply_changes=True)
        assert self.book.count_bids() == 1
        assert self.book.count_asks() == 0
        assert self.book.get_bids()[0].timestamp == 2
        assert self.book.get_bids()[0].counterparty == 'Trader2'

    def test_one_full_execution(self):
        quantity = 10
        price = 42.0
        attacking_order = ServerOrder(Sell(), self.instrument.identifier, quantity, price, 'Trader1')
        attacked_order = ServerOrder(Buy(), self.instrument.identifier, quantity, price, 'Trader2')
        self.book.on_new_order(attacked_order, apply_changes=True)
        self.book.on_new_order(attacking_order, apply_changes=True)
        assert self.book.count_bids() == 0
        assert self.book.count_asks() == 0
        assert attacking_order.executed_quantity, quantity
        assert attacked_order.executed_quantity, quantity
        assert attacking_order.get_remaining_quantity() == 0
        assert attacked_order.get_remaining_quantity() == 0

    def test_one_partial_execution(self):
        attacking_quantity = 20
        attacked_quantity = 10
        price = 42.0
        attacking_order = ServerOrder(Buy(), self.instrument.identifier, attacking_quantity, price, 'Trader1')
        attacked_order = ServerOrder(Sell(), self.instrument.identifier, attacked_quantity, price, 'Trader2')
        self.book.on_new_order(attacked_order, apply_changes=True)
        self.book.on_new_order(attacking_order, apply_changes=True)
        assert self.book.count_bids() == 1
        assert self.book.count_asks() == 0
        assert attacking_order.executed_quantity == attacking_quantity - attacked_quantity
        assert attacked_order.executed_quantity == attacked_quantity
        assert attacking_order.get_remaining_quantity() == attacking_quantity - attacked_quantity
        assert attacked_order.get_remaining_quantity() == 0

    def test_multiple_partial_executions(self):
        attacking_quantity = 50
        attacked_quantity = 10
        price = 42.0
        attacking_order = ServerOrder(Buy(), self.instrument.identifier, attacking_quantity, price, 'Trader1')
        attacked_orders = []
        for _ in list(range(5)):
            attacked_order = ServerOrder(Sell(), self.instrument.identifier, attacked_quantity, price, 'Trader2')
            attacked_orders.append(attacked_order)
            self.book.on_new_order(attacked_order, apply_changes=True)
        self.book.on_new_order(attacking_order, apply_changes=True)
        assert self.book.count_bids() == 0
        assert self.book.count_asks() == 0
        assert attacking_order.executed_quantity == attacking_quantity
        assert attacking_order.get_remaining_quantity() == 0
        for attacked_order in attacked_orders:
            assert attacked_order.executed_quantity == attacked_quantity
            assert attacked_order.get_remaining_quantity() == 0
