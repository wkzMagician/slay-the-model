"""
Colorless Uncommon Skill card - Enlightenment
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Enlightenment(Card):
    """Reduce cost of all cards in hand to 1 energy"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        from engine.game_state import game_state

        super().on_play(targets)

        actions = []
        # Reduce cost of all cards in hand to 1
        if game_state.player and hasattr(game_state.player, "card_manager"):
            hand_cards = list(game_state.player.card_manager.get_pile("hand"))
            for card in hand_cards:
                if self.upgrade_level == 0:
                    # Set temporary cost to 1 for all cards
                    card.cost_until_end_of_turn = 1
                else:
                    # last for combat
                    card.cost = 1

        from engine.game_state import game_state

        add_actions(actions)

        return
