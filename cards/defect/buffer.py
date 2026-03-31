"""Defect rare power card - Buffer."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.buffer import BufferPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Buffer(Card):
    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 2
    base_magic = {"stacks": 1}
    upgrade_magic = {"stacks": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(BufferPower(amount=self.get_magic_value("stacks"), owner=game_state.player), game_state.player))
