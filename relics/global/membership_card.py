"""
Membership Card - Shop relic
Cards in shop cost 25% less.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class MembershipCard(Relic):
    """Membership Card - Cards in shop cost 25% less"""

    def __init__(self):
        super().__init__()
        self.idstr = "MembershipCard"
        self.name_key = "relics.membership_card.name"
        self.description_key = "relics.membership_card.description"
        self.rarity = RarityType.SHOP

        # Track discount amount
        self.discount_percent = 0.25  # 25% discount

    def on_card_buy_cost(self, card, original_cost):
        """Apply 25% discount to card purchases in shop"""
        # The discount is already applied in shop.py
        # This is handled in the shop pricing logic
        return original_cost * self.discount_percent
