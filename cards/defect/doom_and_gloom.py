"""Defect uncommon attack card - Doom and Gloom."""

from typing import List

from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.dark import DarkOrb
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class DoomAndGloom(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    base_target_type = TargetType.ENEMY_ALL

    base_cost = 2
    base_damage = 10
    upgrade_damage = 14

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_action

        add_action(AddOrbAction(DarkOrb()))
