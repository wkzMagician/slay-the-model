"""Defect uncommon power card - Defragment."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.focus import FocusPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Defragment(Card):
    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"focus": 1}
    upgrade_magic = {"focus": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(FocusPower(amount=self.get_magic_value("focus"), owner=game_state.player), game_state.player))
