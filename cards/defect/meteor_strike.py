"""Defect rare attack card - Meteor Strike."""

from typing import List

from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.plasma import PlasmaOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class MeteorStrike(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.RARE

    base_cost = 5
    base_damage = 24
    upgrade_damage = 30

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_actions

        add_actions([AddOrbAction(PlasmaOrb()), AddOrbAction(PlasmaOrb()), AddOrbAction(PlasmaOrb())])
