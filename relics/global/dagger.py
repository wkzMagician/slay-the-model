"""
Dagger - Rare relic
Gain 1 Strength at the start of combat.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class Dagger(Relic):
    """Dagger - Gain 1 Strength at start of combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "Dagger"
        self.name_key = "relics.dagger.name"
        self.description_key = "relics.dagger.description"
        self.rarity = RarityType.RARE

    def on_combat_start(self):
        """Apply 1 Strength at start of combat"""
        # This would be handled via status effects
        pass
