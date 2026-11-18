"""
Colorless Uncommon Skill card - Deep Breath
"""
from typing import List
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DeepBreath(Card):
    """Shuffle discard into draw pile, draw cards"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_draw = 1

    upgrade_draw = 2

    def on_play(self, targets: List[Creature] = []):
        from actions.card_shuffle import DrawAfterShuffleAction, queue_active_shuffle
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        if game_state.player and game_state.player.card_manager.get_pile("discard_pile"):
            queue_active_shuffle()
        add_action(DrawAfterShuffleAction(count=self.draw))
