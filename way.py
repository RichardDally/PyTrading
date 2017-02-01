class Way:
    BUY = 0
    SELL = 1

    def get_opposite_way(self, way):
        if way == Way.BUY:
            return Way.SELL
        elif way == Way.SELL:
            return Way.BUY
        raise Exception('Way is invalid')
