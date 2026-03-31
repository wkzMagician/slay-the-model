"""Defect uncommon skill card - Genetic Algorithm."""

from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class GeneticAlgorithm(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_block = 1
    base_exhaust = True
    base_magic = {"growth": 2}
    upgrade_magic = {"growth": 3}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        self._block += self.get_magic_value("growth")
        origin_card = getattr(self, "origin_card", None)
        if origin_card is not None and origin_card is not self:
            origin_card._block += self.get_magic_value("growth")
