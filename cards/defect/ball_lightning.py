"""Defect common attack card - Ball Lightning."""

from typing import List

from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.lightning import LightningOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BallLightning(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 7
    upgrade_damage = 10

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_action

        add_action(AddOrbAction(LightningOrb()))
