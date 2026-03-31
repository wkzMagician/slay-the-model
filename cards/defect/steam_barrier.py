"""Defect uncommon skill card - Steam Barrier."""

from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class SteamBarrier(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_block = 6
    upgrade_block = 8

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        self._block = max(0, self._block - 1)
