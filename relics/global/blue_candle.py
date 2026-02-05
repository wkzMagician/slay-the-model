"""
Blue Candle - Boss relic
At start of combat, gain 1 Artifact.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class BlueCandle(Relic):
    """Blue Candle - Gain 1 Artifact at start of combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "BlueCandle"
        self.name_key = "relics.blue_candle.name"
        self.description_key = "relics.blue_candle.description"
        self.rarity = RarityType.BOSS

    def on_combat_start(self):
        """Gain 1 Artifact at start of combat"""
        # This would apply an artifact status effect
        # For now, this is a placeholder
        pass
