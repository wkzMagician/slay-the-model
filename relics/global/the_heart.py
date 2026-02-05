"""
The Heart - Boss relic
Lose 1 HP at the end of your turn.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class TheHeart(Relic):
    """The Heart - Boss relic"""

    def __init__(self):
        super().__init__()
        self.idstr = "TheHeart"
        self.name_key = "relics.the_heart.name"
        self.description_key = "relics.the_heart.description"
        self.rarity = RarityType.BOSS

    def on_player_end(self):
        """Lose 1 HP at end of your turn"""
        # This would apply HP reduction
        # For now, this is a placeholder
        pass
