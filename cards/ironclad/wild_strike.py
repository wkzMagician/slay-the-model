"""
Ironclad Common Attack card - Wild Strike
"""

from typing import List
from actions.base import Action
from actions.card import AddCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class WildStrike(Card):
    """Deal damage and shuffle Wound into draw pile"""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 12

    upgrade_damage = 17

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Add Wound status card to draw pile
        from cards.colorless.wound import Wound
        actions.append(AddCardAction(card=Wound(), dest_pile="draw_pile"))

        return actions
