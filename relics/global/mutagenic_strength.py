"""
Mutagenic Strength - Rare relic
Gain 1 Strength at the end of your turn.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class MutagenicStrength(Relic):
    """Mutagenic Strength - Gain 1 Strength at end of your turn"""

    def __init__(self):
        super().__init__()
        self.idstr = "MutagenicStrength"
        self.name_key = "relics.mutagenic_strength.name"
        self.description_key = "relics.mutagenic_strength.description"
        self.rarity = RarityType.RARE

    def on_player_end(self):
        """Gain 1 Strength at end of your turn"""
        # This would be handled via status effects
        pass
