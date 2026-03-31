"""Defect uncommon skill card - Auto Shields."""

from typing import List

from actions.combat import GainBlockAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class AutoShields(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_block = 11
    upgrade_block = 15

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        if game_state.player.block == 0:
            add_action(GainBlockAction(block=self.block, target=game_state.player))
