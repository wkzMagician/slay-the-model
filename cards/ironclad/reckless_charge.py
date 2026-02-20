"""
Ironclad Uncommon Attack card - Reckless Charge
"""

from typing import List
from actions.base import Action
from actions.card import AddCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class RecklessCharge(Card):
    """Deal damage, shuffle Dazed into draw pile"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_damage = 7

    upgrade_damage = 10

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        actions = super().on_play(targets)

        # Shuffle Dazed into draw pile
        from cards.colorless import Dazed
        actions.append(AddCardAction(card=Dazed(), dest_pile="draw_pile"))

        return actions
