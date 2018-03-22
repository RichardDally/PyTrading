from exceptions import InvalidWay


class WayEnum:
    def __init__(self):
        pass
    BUY = 0
    SELL = 1


class OrderWay:
    def __init__(self, way):
        if way not in (WayEnum.BUY, WayEnum.SELL):
            raise InvalidWay(way)
        self.way = way

    def __str__(self):
        if self.way == WayEnum.BUY:
            return 'Buy'
        if self.way == WayEnum.SELL:
            return 'Sell'
        raise InvalidWay()

    def __cmp__(self, other):
        return self.way == other.way

    def __eq__(self, other):
        return self.way == other.way

    @staticmethod
    def get_opposite_way(order_way):
        if order_way.way == WayEnum.BUY:
            return Sell()
        if order_way.way == WayEnum.SELL:
            return Buy()
        raise InvalidWay(order_way.way)


class Buy(OrderWay):
    def __init__(self):
        OrderWay.__init__(self, WayEnum.BUY)


class Sell(OrderWay):
    def __init__(self):
        OrderWay.__init__(self, WayEnum.SELL)
