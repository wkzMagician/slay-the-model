"""Silent common skill card - Dodge and Roll."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.next_turn_block import NextTurnBlockPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DodgeAndRoll(Card):
    """Gain block now and next turn."""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_block = 4

    upgrade_block = 6

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(NextTurnBlockPower(amount=self.block, owner=game_state.player), game_state.player)
        ])
