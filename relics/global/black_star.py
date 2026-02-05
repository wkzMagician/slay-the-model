"""
Black Star - Uncommon relic
Every 3rd card played costs 1 less.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class BlackStar(Relic):
    """Every 3rd card played costs 1 less energy"""

    def __init__(self):
        super().__init__()
        self.idstr = "BlackStar"
        self.name_key = "relics.black_star.name"
        self.description_key = "relics.black_star.description"
        self.rarity = RarityType.UNCOMMON
