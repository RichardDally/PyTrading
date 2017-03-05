import capnp
import referential_capnp
import orderbookfullsnapshot_capnp
from orderbook import OrderBook
from instrument import Instrument
from referential import Referential
from staticdata import StaticData

class Serialization:
    @staticmethod
    def encode_referential(referential):
        referentialMessage = referential_capnp.Referential.new_message()
        instrumentsSize = len(referential)
        if instrumentsSize:
            instrumentList = referentialMessage.init('instruments', instrumentsSize)
            for index, instrument in enumerate(referential.get_instruments()):
                instrumentList[index].id = instrument.id
                instrumentList[index].name = instrument.name
                instrumentList[index].isin = instrument.isin
                instrumentList[index].currencyId = instrument.currencyId
        return referentialMessage

    @staticmethod
    def decode_referential(encodedReferential):
        referential = Referential()
        referentialMessage = referential_capnp.Referential.from_bytes(encodedReferential)
        for decodedInstrument in referentialMessage.instruments:
            instrument = Instrument(id=decodedInstrument.id,
                                    name=decodedInstrument.name,
                                    isin=decodedInstrument.isin,
                                    currencyId=decodedInstrument.currencyId)
            referential.add_instrument(instrument)
        return referential

    @staticmethod
    def encode_orders(orderbookMessage, orderbook, side):
        ordersCount = eval('orderbook.count_{}()'.format(side))
        if ordersCount:
            orders = orderbookMessage.init(side, ordersCount)
            for index, order in enumerate(eval('orderbook.get_{}()'.format(side))):
                orders[index].orderId = order.id
                orders[index].way = order.way
                orders[index].quantity = order.quantity
                orders[index].price = order.price
                orders[index].timestamp = order.timestamp

    @staticmethod
    def encode_orderbookfullsnapshot(orderbook):
        orderbookMessage = orderbookfullsnapshot_capnp.OrderBookFullSnapshot.new_message()
        orderbookMessage.instrumentId = orderbook.instrument.id
        orderbookMessage.statistics.lastPrice = orderbook.last
        orderbookMessage.statistics.highPrice = orderbook.high
        orderbookMessage.statistics.lowPrice = orderbook.low
        Serialization.encode_orders(orderbookMessage, orderbook, 'bids')
        Serialization.encode_orders(orderbookMessage, orderbook, 'asks')
        return orderbookMessage


    @staticmethod
    def decode_orders(decodedOrderBook, orderbook, side):
        for decodedOrder in eval('decodedOrderBook.{}'.format(side)):
            order = Order(id=decodedOrder.orderId,
                          way=decodedOrder.way,
                          instrument=StaticData.get_instrument(decodedOrder.instrumentId),
                          quantity=decodedOrder.quantity,
                          price=decodedOrder.price,
                          counterparty=decodedOrder.counterparty,
                          timestamp=decodedOrder.timestamp)
            eval('orderbook.{}.append(order)'.format(side))

    @staticmethod
    def decode_orderbookfullsnapshot(encodedOrderBookFullSnapshot):
        decodedOrderBook = orderbookfullsnapshot_capnp.OrderBookFullSnapshot.from_bytes(encodedOrderBookFullSnapshot)
        orderbook = OrderBook(StaticData.get_instrument(decodedOrderBook.instrumentId))
        orderbook.last = decodedOrderBook.statistics.lastPrice
        orderbook.high = decodedOrderBook.statistics.highPrice
        orderbook.low = decodedOrderBook.statistics.lowPrice
        Serialization.decode_orders(decodedOrderBook, orderbook, 'bids')
        Serialization.decode_orders(decodedOrderBook, orderbook, 'asks')
        return orderbook
