"""
Colorless Uncommon Skill card - Madness
"""

from typing import List
from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Madness(Card):
    """Reduce cost of random card to 0 this combat, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_exhaust = True

    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state
        import random

        actions = super().on_play(targets)

        # Reduce cost of a random card in hand to 0 for this combat
        if game_state.player and hasattr(game_state.player, "card_manager"):
            hand_cards = list(game_state.player.card_manager.get_pile("hand"))
            if hand_cards:
                # Select random card from hand
                random_card = random.choice(hand_cards)
                # Set its cost to 0 for the entire combat
                # We need a way to track "cost 0 for this combat"
                # For now, use a very negative temp_cost as a marker
                # A proper implementation would use a power or special flag
                random_card.cost = 0

        return actions
