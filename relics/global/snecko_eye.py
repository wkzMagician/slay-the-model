"""
Snecko Eye - Boss relic
Enemies start with 3 less HP and play random cards.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class SneckoEye(Relic):
    """Snecko Eye - Boss relic"""

    def __init__(self):
        super().__init__()
        self.idstr = "SneckoEye"
        self.name_key = "relics.snecko_eye.name"
        self.description_key = "relics.snecko_eye.description"
        self.rarity = RarityType.BOSS

    def on_combat_start(self):
        """Apply enemy debuff at start of combat"""
        # Enemies have 3 less HP (simplified approach)
        # In a full implementation, this would apply to each enemy
        # For now, this is a placeholder
        pass
