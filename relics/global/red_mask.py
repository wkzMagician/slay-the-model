"""
Red Mask - Rare relic
Gain 1 Strength at the end of each combat.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class RedMask(Relic):
    """Red Mask - Gain 1 Strength at end of combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "RedMask"
        self.name_key = "relics.red_mask.name"
        self.description_key = "relics.red_mask.description"
        self.rarity = RarityType.RARE

    def on_combat_end(self, result):
        """Gain 1 Strength after combat if won"""
        if result == "WIN":
            # This would add a strength status
            pass

        return None
