"""Silent rare skill card - Burst."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.burst import BurstPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Burst(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 1
    base_magic = {"copies": 1}
    upgrade_magic = {"copies": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([ApplyPowerAction(BurstPower(amount=self.get_magic_value("copies"), owner=game_state.player), game_state.player)])
