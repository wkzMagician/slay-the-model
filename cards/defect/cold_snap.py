"""Defect common attack card - Cold Snap."""

from typing import List

from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.frost import FrostOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class ColdSnap(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 6
    upgrade_damage = 9

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_action

        add_action(AddOrbAction(FrostOrb()))
