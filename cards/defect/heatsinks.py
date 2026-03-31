"""Defect uncommon power card - Heatsinks."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.heatsinks import HeatsinksPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Heatsinks(Card):
    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"draw": 1}
    upgrade_magic = {"draw": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(HeatsinksPower(amount=self.get_magic_value("draw"), owner=game_state.player), game_state.player))
