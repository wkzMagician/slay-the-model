"""
The Courier - Boss relic
Restock shop relic purchases at 80% price.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class TheCourier(Relic):
    """The Courier - Restock shop at 80% price"""

    def __init__(self):
        super().__init__()
        self.idstr = "TheCourier"
        self.name_key = "relics.the_courier.name"
        self.description_key = "relics.the_courier.description"
        self.rarity = RarityType.BOSS

    def on_shop_open(self):
        """Reset restock multiplier when shop opens"""
        # This would be handled in shop.py via relic check
        pass

    def on_bought_item(self, shop_item):
        """Apply 80% price to relic item"""
        # Check if it's a relic (not a card or potion)
        if hasattr(shop_item, 'item') and hasattr(shop_item.item, '__class__'):
            # Apply 80% price multiplier
            shop_item.price_multiplier = 0.8

        return None
