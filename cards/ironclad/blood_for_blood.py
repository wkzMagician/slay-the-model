"""
Ironclad Uncommon Attack card - Blood for Blood
"""

from typing import List
from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BloodForBlood(Card):
    """Deal damage, costs less for each HP lost this combat"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 4
    base_damage = 18

    upgrade_damage = 22

    def on_damage_taken(self, damage: int, source: Creature, card: Card, damage_type: str) -> List[Action]:
        """Track HP taken to reduce card cost"""
        # Reduce cost by 1 each time damage is taken (minimum 0)
        self._cost = max(0, self._cost - 1)
        return []  # Return empty list, just updating cost
