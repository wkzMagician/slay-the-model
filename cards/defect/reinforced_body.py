"""Defect rare skill card - Reinforced Body."""

from typing import List

from actions.combat import GainBlockAction
from cards.base import COST_X, Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class ReinforcedBody(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = COST_X
    base_magic = {"block": 7}
    upgrade_magic = {"block": 9}

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        x_value = self.get_effective_x()
        add_action(GainBlockAction(block=self.get_magic_value("block") * x_value, target=game_state.player))
