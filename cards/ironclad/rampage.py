"""
Ironclad Uncommon Attack card - Rampage
"""

from typing import List
from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Rampage(Card):
    """Deal damage, increase damage this combat"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_damage = 8

    base_magic = {"damage_gain": 5}
    upgrade_magic = {"damage_gain": 8}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        actions = super().on_play(targets)

        # Increase this card's damage for the combat
        damage_increase = self.get_magic_value("damage_gain")
        self._damage += damage_increase

        return actions
