"""
Hook and Rope - Uncommon relic
First 3 cards cost 0 instead of 1, 2, 3.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class HookAndRope(Relic):
    """Hook and Rope - First 3 cards cost 0"""

    def __init__(self):
        super().__init__()
        self.idstr = "HookAndRope"
        self.name_key = "relics.hook_and_rope.name"
        self.description_key = "relics.hook_and_rope.description"
        self.rarity = RarityType.UNCOMMON

    def on_card_play_cost(self, card, player, original_cost):
        """Modify card cost - first 3 cards cost 0"""
        from engine.game_state import game_state

        # Get deck to count cards played
        deck = game_state.player.card_manager.get_pile('deck')

        # Count how many cards have been played this combat
        # This is a simplified approach
        cards_played = 0
        for status in game_state.combat_state.status_effects.values():
            if status.get('cards_played', 0) > cards_played:
                cards_played = status['cards_played']

        # If fewer than 3 cards played, first card costs 0
        if cards_played < 3:
            return 0

        # Otherwise, use original cost logic
        return original_cost
