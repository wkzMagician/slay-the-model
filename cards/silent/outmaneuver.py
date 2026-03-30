"""Silent common skill card - Outmaneuver."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.energized import EnergizedPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Outmaneuver(Card):
    """Gain additional energy next turn."""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_magic = {"energy": 2}

    upgrade_magic = {"energy": 3}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(EnergizedPower(amount=self.get_magic_value("energy"), owner=game_state.player), game_state.player)
        ])
