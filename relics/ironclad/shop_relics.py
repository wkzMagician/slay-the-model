"""Shop Ironclad relics."""
from relics.base import Relic
from utils.registry import register
from utils.types import RarityType


@register("relic")
class MembershipCard(Relic):
    """Cards in shop cost 25% less"""
    rarity = RarityType.SHOP

    def __init__(self):
        super().__init__()
        self.discount_percent = 0.25  # 25% discount
