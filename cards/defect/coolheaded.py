"""Defect common skill card - Coolheaded."""

from typing import List

from actions.card import DrawCardsAction
from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.frost import FrostOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Coolheaded(Card):
    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_draw = 1
    upgrade_draw = 2

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_action

        add_action(AddOrbAction(FrostOrb()))
