"""Defect uncommon skill card - Glacier."""

from typing import List

from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.frost import FrostOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Glacier(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_block = 7
    upgrade_block = 10

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_actions

        add_actions([AddOrbAction(FrostOrb()), AddOrbAction(FrostOrb())])
