"""Defect rare power card - Machine Learning."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.machine_learning import MachineLearningPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class MachineLearning(Card):
    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 1
    base_magic = {"draw": 1}
    upgrade_innate = True

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(MachineLearningPower(amount=self.get_magic_value("draw"), owner=game_state.player), game_state.player))
