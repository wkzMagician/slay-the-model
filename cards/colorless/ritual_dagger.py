"""
Colorless Special Attack card - Ritual Dagger
"""

from typing import List
from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class RitualDagger(Card):
    """Deal damage, permanently increase damage on kill, Exhaust"""

    card_type = CardType.ATTACK
    rarity = RarityType.SPECIAL
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_damage = 15
    base_magic = {"fatal_bonus": 3, "damage_increase": 3}
    base_exhaust = True

    upgrade_magic = {"fatal_bonus": 5, "damage_increase": 5}

    def on_fatal(self) -> List[Action]:
        """If this kills enemy, permanently increase this Card's damage"""
        actions = []

        fatal_bonus = self.get_magic_value(
            "damage_increase",
            self.get_magic_value("fatal_bonus"),
        )
        # Permanently increase this card instance's damage
        self._damage += fatal_bonus

        return actions
