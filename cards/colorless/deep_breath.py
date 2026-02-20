"""
Colorless Uncommon Skill card - Deep Breath
"""

from typing import List
from actions.base import Action
from actions.card import DrawCardsAction
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

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state
        from actions.card import ShuffleAction

        actions = super().on_play(targets)

        # Shuffle discard pile into draw pile
        actions.append(ShuffleAction())

        return actions
