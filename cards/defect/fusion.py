"""Defect uncommon skill card - Fusion."""

from typing import List

from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.plasma import PlasmaOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Fusion(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 2
    upgrade_cost = 1

    def on_play(self, targets: List[Creature] = []):
        from engine.runtime_api import add_action

        add_action(AddOrbAction(PlasmaOrb()))

