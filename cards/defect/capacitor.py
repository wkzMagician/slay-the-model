"""Defect uncommon power card - Capacitor."""

from typing import List

from actions.orb import IncreaseOrbSlotsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Capacitor(Card):
    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"slots": 2}
    upgrade_magic = {"slots": 3}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_action

        add_action(IncreaseOrbSlotsAction(amount=self.get_magic_value("slots")))
