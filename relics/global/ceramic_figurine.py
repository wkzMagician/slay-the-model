"""
Ceramic Figurine - Uncommon relic
At start of combat, draw 2 cards.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class CeramicFigurine(Relic):
    """Ceramic Figurine - Draw 2 cards at start of combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "CeramicFigurine"
        self.name_key = "relics.ceramic_figurine.name"
        self.description_key = "relics.ceramic_figurine.description"
        self.rarity = RarityType.UNCOMMON

    def on_combat_start(self):
        """Draw 2 cards at start of combat"""
        from actions.card import DrawCardsAction

        # Create a draw cards action with 2 cards
        return DrawCardsAction(count=2)
