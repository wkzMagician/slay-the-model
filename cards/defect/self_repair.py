"""Defect uncommon power card - Self Repair."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.self_repair import SelfRepairPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class SelfRepair(Card):
    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"heal": 7}
    upgrade_magic = {"heal": 10}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(SelfRepairPower(amount=self.get_magic_value("heal"), owner=game_state.player), game_state.player))
