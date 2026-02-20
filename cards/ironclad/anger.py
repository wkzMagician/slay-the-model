"""
Ironclad Common Attack card - Anger
"""

from typing import List
from actions.base import Action
from actions.card import AddCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Anger(Card):
    """Deal damage and add a copy to discard pile"""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 0
    base_damage = 6

    upgrade_damage = 8

    def on_play(self, target: Creature | None = None) -> List[Action]:
        return super().on_play(target) + [AddCardAction(card=self, dest_pile="discard_pile")]
