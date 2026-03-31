"""Defect uncommon skill card - Chill."""

from typing import List

from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.frost import FrostOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Chill(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_exhaust = True
    upgrade_innate = True

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        enemies = game_state.current_combat.enemies if game_state.current_combat is not None else []
        for _ in enemies:
            add_action(AddOrbAction(FrostOrb()))
