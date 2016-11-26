from way import Way                                                                                                                                                                                                
from order import Order
from currency import Currency
from orderbook import OrderBook
from instrument import Instrument

tr = OrderBook()

if 1:
    euroCurrency = Currency(0, 'EUR')
    carrefourInstrument = Instrument(0, 'Carrefour', euroCurrency, 'FR0000120172')
    tr.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 20.0, 'Trader4'))
    tr.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 20.0, 'Trader5'))
    tr.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 20.0, 'Trader2'))
    print(tr)
    tr.on_new_order(Order(Way.BUY, carrefourInstrument, 50, 20.0, 'Trader1'))

if 0:
    tr.on_new_order(Order(Way.BUY, carrefourInstrument, 50, 21.0, 'Trader1'))
    tr.on_new_order(Order(Way.BUY, carrefourInstrument, 50, 20.0, 'Trader2'))
    tr.on_new_order(Order(Way.BUY, carrefourInstrument, 50, 19.0, 'Trader3'))
    tr.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 22.0, 'Trader4'))
    tr.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 23.0, 'Trader5'))
    tr.on_new_order(Order(Way.SELL, carrefourInstrument, 50, 24.0, 'Trader6'))

print(tr)