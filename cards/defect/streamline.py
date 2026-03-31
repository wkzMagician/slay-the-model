"""Defect common attack card - Streamline."""

from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Streamline(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 2
    base_damage = 15
    upgrade_damage = 20

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        self._cost = max(0, self._cost - 1)
