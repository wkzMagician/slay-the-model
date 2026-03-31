"""Defect uncommon skill card - Double Energy."""

from typing import List

from actions.combat import GainEnergyAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DoubleEnergy(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_exhaust = True
    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(GainEnergyAction(energy=game_state.player.energy))
