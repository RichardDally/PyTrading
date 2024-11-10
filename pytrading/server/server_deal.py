from pytrading import ServerOrder
from pytrading import generate_unique_identifier
from pytrading import generate_timestamp


class ServerDeal:
    def __init__(self, attacking_order: ServerOrder, attacked_order: ServerOrder, executed_quantity: float) -> None:
        assert attacking_order.instrument_identifier == attacked_order.instrument_identifier,\
            "Instrument identifier must match"
        self.identifier = generate_unique_identifier()
        self.instrument_identifier = attacking_order.instrument_identifier
        self.attacker = attacking_order.counterparty
        self.attacked = attacked_order.counterparty
        self.quantity = executed_quantity
        self.price = attacked_order.price
        self.timestamp = generate_timestamp()
