"""Defect uncommon attack card - Sunder."""

from typing import List

from actions.combat import GainEnergyAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Sunder(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 3
    base_damage = 24
    upgrade_damage = 32

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)

    def on_fatal(self, damage: int, target=None, card=None, damage_type: str = "direct"):
        from engine.runtime_api import add_action

        if card is self and target is not None:
            add_action(GainEnergyAction(energy=3))
