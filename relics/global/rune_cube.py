"""
Runic Cube - Boss relic
Draw 2 random cards from a specific card pool each time you play a card.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class RuneCube(Relic):
    """Runic Cube - Draw 2 random cards from specific pool when playing cards"""

    def __init__(self):
        super().__init__()
        self.idstr = "RuneCube"
        self.name_key = "relics.rune_cube.name"
        self.description_key = "relics.rune_cube.description"
        self.rarity = RarityType.BOSS

    def on_card_played(self, card, player):
        """Trigger when a card is played"""
        # In a full implementation, this would track card pool
        # and draw 2 random cards from that pool
        # For now, this is a simplified approach
        pass
