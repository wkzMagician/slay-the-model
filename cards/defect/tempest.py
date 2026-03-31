"""Defect uncommon skill card - Tempest."""

from typing import List

from actions.orb import AddOrbAction
from cards.base import COST_X, Card
from entities.creature import Creature
from orbs.lightning import LightningOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Tempest(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = COST_X
    base_exhaust = True
    base_magic = {"bonus": 0}
    upgrade_magic = {"bonus": 1}

    def on_play(self, targets: List[Creature] = []):
        from engine.runtime_api import add_action

        total = self.get_effective_x() + self.get_magic_value("bonus")
        for _ in range(total):
            add_action(AddOrbAction(LightningOrb()))
