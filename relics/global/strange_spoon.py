"""
Strange Spoon - Uncommon relic
At end of combat, gain 1 Strength.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class StrangeSpoon(Relic):
    """Strange Spoon - Gain 1 Strength at end of combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "StrangeSpoon"
        self.name_key = "relics.strange_spoon.name"
        self.description_key = "relics.strange_spoon.description"
        self.rarity = RarityType.UNCOMMON

    def on_combat_end(self, result):
        """Gain 1 Strength after combat if won"""
        if result == "WIN":
            # This would apply via status effects
            # In a full implementation, this would add a strength status
            pass

        return None
