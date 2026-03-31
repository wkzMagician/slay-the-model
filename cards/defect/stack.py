"""Defect common skill card - Stack."""

from typing import List

from actions.combat import GainBlockAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Stack(Card):
    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    upgrade_magic = {"bonus": 3}

    @property
    def block(self) -> int:
        from engine.game_state import game_state

        player = getattr(game_state, "player", None)
        if player is None:
            return self.get_magic_value("bonus", 0)
        discard_count = len(player.card_manager.get_pile("discard_pile"))
        return discard_count + self.get_magic_value("bonus", 0)

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(GainBlockAction(block=self.block, target=game_state.player))
