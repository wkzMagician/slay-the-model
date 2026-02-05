"""
Vajra - Common relic
Gain 1 Strength at the start of each combat.
"""
from entities.player import Player
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class Vajra(Relic):
    """Gain 1 Strength at start of combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "Vajra"
        self.name_key = "relics.vajra.name"
        self.description_key = "relics.vajra.description"
        self.rarity = RarityType.COMMON

    def on_combat_start(self):
        """Apply 1 Strength at start of combat"""
        # Strength is applied via status effects
        # This will be handled by the combat system
        return None
