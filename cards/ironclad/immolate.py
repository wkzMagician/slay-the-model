"""
Ironclad Rare Attack card - Immolate
"""

from typing import List
from actions.base import Action
from actions.card import AddCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Immolate(Card):
    """Deal damage to ALL enemies, add Burn"""

    card_type = CardType.ATTACK
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_ALL

    base_cost = 2
    base_damage = 21

    upgrade_damage = 28

    def on_play(self, target: Creature | None = None) -> List[Action]:
        actions = super().on_play(target)

        # Add Burn status to discard pile
        from cards.colorless import Burn
        actions.append(AddCardAction(card=Burn(), dest_pile="discard"))

        return actions
