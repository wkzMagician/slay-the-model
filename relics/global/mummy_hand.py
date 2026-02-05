"""
Mummy Hand - Rare relic
Draw 1 additional card each turn.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class MummyHand(Relic):
    """Mummy Hand - Draw 1 extra card each turn"""

    def __init__(self):
        super().__init__()
        self.idstr = "MummyHand"
        self.name_key = "relics.mummy_hand.name"
        self.description_key = "relics.mummy_hand.description"
        self.rarity = RarityType.RARE

    def on_turn_start(self):
        """Draw 1 extra card each turn"""
        from actions.card import DrawCardsAction

        return DrawCardsAction(count=1)
