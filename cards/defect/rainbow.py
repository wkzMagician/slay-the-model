"""Defect rare skill card - Rainbow."""

from typing import List

from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.dark import DarkOrb
from orbs.frost import FrostOrb
from orbs.lightning import LightningOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Rainbow(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 2
    base_exhaust = True
    upgrade_exhaust = False

    def on_play(self, targets: List[Creature] = []):
        from engine.runtime_api import add_actions

        add_actions([AddOrbAction(LightningOrb()), AddOrbAction(FrostOrb()), AddOrbAction(DarkOrb())])
