"""Defect rare skill card - Multi-Cast."""

from typing import List

from actions.orb import EvokeOrbAction
from cards.base import COST_X, Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class MultiCast(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = COST_X
    base_magic = {"bonus": 0}
    upgrade_magic = {"bonus": 1}

    def on_play(self, targets: List[Creature] = []):
        from engine.runtime_api import add_action

        add_action(EvokeOrbAction(index=0, times=self.get_effective_x() + self.get_magic_value("bonus")))
