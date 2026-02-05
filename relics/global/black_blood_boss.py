"""
Black Blood - Boss relic
Gain 1 Strength at the end of your turn.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class BlackBloodBoss(Relic):
    """Black Blood - Gain 1 Strength at end of your turn"""

    def __init__(self):
        super().__init__()
        self.idstr = "BlackBlood"
        self.name_key = "relics.black_blood_boss.name"
        self.description_key = "relics.black_blood_boss.description"
        self.rarity = RarityType.BOSS

    def on_player_end(self):
        """Gain 1 Strength at end of your turn"""
        # This would add a strength status
        pass
