"""
Frozen Core - Boss relic
Draw 2 cards at the end of your turn.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class FrozenCore(Relic):
    """Frozen Core - Draw 2 cards at end of your turn"""

    def __init__(self):
        super().__init__()
        self.idstr = "FrozenCore"
        self.name_key = "relics.frozen_core.name"
        self.description_key = "relics.frozen_core.description"
        self.rarity = RarityType.BOSS

    def on_player_end(self):
        """Draw 2 cards at end of player's turn"""
        from actions.card import DrawCardsAction

        # Create a draw cards action with 2 cards
        return DrawCardsAction(count=2)
