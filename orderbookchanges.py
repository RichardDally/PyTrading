class OrderBookChanges:
    def __init__(self, **kwargs):
        self.order_to_add = kwargs.get('order_to_add', [])
        self.order_to_remove = kwargs.get('order_to_remove', [])
        self.deals_to_add = kwargs.get('deals_to_add', [])

    @staticmethod
    def stringify_objects_list(objects_list):
        return "\n".join([str(obj) for obj in objects_list])

    def __str__(self):
        """
        TODO: fix unnecessary last line feed (cosmetic)
        """
        result = f"Insert orders:\n{self.stringify_objects_list(self.order_to_add)}\n" if self.order_to_add else ""
        result += f"Delete orders:\n{self.stringify_objects_list(self.order_to_remove)}\n" if self.order_to_remove else ""
        result += f"Insert deals:\n{self.stringify_objects_list(self.deals_to_add)}" if self.deals_to_add else ""
        return result
