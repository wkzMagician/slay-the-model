"""
Vajra - Rare relic
Start combat with 1 Strength.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class VajraBoss(Relic):
    """Vajra - Start combat with 1 Strength"""

    def __init__(self):
        super().__init__()
        self.idstr = "VajraBoss"
        self.name_key = "relics.vajra_boss.name"
        self.description_key = "relics.vajra_boss.description"
        self.rarity = RarityType.RARE

    def on_combat_start(self):
        """Apply 1 Strength at start of combat"""
        # This would be handled via status effects
        pass
