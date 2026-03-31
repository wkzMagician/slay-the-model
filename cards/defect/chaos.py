"""Defect uncommon skill card - Chaos."""

from typing import List

from actions.base import LambdaAction
from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.dark import DarkOrb
from orbs.frost import FrostOrb
from orbs.lightning import LightningOrb
from orbs.plasma import PlasmaOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Chaos(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"orbs": 1}
    upgrade_magic = {"orbs": 2}

    def on_play(self, targets: List[Creature] = []):
        import random
        from engine.runtime_api import add_action

        orb_types = [LightningOrb, FrostOrb, DarkOrb, PlasmaOrb]
        for _ in range(self.get_magic_value("orbs")):
            add_action(AddOrbAction(random.choice(orb_types)()))
