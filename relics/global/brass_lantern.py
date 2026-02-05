"""
Brass Lantern - Uncommon relic
Start each combat with 1 weak applied to all enemies.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class BrassLantern(Relic):
    """Brass Lantern - Weak applied to all enemies at start of combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "BrassLantern"
        self.name_key = "relics.brass_lantern.name"
        self.description_key = "relics.brass_lantern.description"
        self.rarity = RarityType.UNCOMMON

    def on_combat_start(self):
        """Apply 1 Weak to all enemies at start of combat"""
        # In a full implementation, this would iterate through all enemies
        # and apply weak status effect
        # For now, this is a simplified approach
        pass
