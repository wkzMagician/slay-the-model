"""Defect common skill card - Charge Battery."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.energized import EnergizedPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class ChargeBattery(Card):
    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_block = 7
    upgrade_block = 10

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(EnergizedPower(amount=1, owner=game_state.player), game_state.player))
