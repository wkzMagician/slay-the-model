"""
Shop Global Relics
Global relics available in the shop.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class MembershipCard(Relic):
    """Cards in shop cost 25% less"""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP
        self.discount_percent = 0.5  # 25% discount