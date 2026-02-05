"""
Akara - Rare relic
Draw 3 cards after each combat.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class Akara(Relic):
    """Akara - Draw 3 cards after each combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "Akara"
        self.name_key = "relics.akara.name"
        self.description_key = "relics.akara.description"
        self.rarity = RarityType.RARE

    def on_combat_end(self, result):
        """Draw 3 cards after combat if won"""
        if result == "WIN":
            from actions.card import DrawCardsAction

            # Create a draw cards action with 3 cards
            return DrawCardsAction(count=3)
