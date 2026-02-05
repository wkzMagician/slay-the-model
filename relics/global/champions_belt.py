"""
Champion's Belt - Boss relic
Cards cost 0 every 5th card played.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class ChampionsBelt(Relic):
    """Champion's Belt - Every 5th card costs 0"""

    def __init__(self):
        super().__init__()
        self.idstr = "ChampionsBelt"
        self.name_key = "relics.champions_belt.name"
        self.description_key = "relics.champions_belt.description"
        self.rarity = RarityType.BOSS

        # Track cards played in this combat
        self.cards_played_this_combat = 0

    def on_card_played(self, card, player):
        """Count cards played, every 5th costs 0"""
        self.cards_played_this_combat += 1

        if self.cards_played_this_combat % 5 == 0:
            # Reset cost to 0
            return 0

        # Otherwise, use original cost
        # This is passed through via player
        return None

    def on_card_play_cost(self, card, player, original_cost):
        """Reset counter at start of combat"""
        self.cards_played_this_combat = 0
        return original_cost
