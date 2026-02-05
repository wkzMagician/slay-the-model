"""
Bag of Preparation - Common relic
Draw 3 additional cards at the start of each combat.
"""
from entities.player import Player
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class BagOfPreparation(Relic):
    """Draw 3 extra cards at start of combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "BagOfPreparation"
        self.name_key = "relics.bag_of_preparation.name"
        self.description_key = "relics.bag_of_preparation.description"
        self.rarity = RarityType.COMMON

    def on_combat_start(self):
        """Draw 3 extra cards at start of combat"""
        from actions.card import DrawCardsAction

        # Create a draw cards action with 3 cards
        # This will be added to combat action queue
        return DrawCardsAction(count=3)
