"""Defect uncommon skill card - Equilibrium."""

from typing import List

from actions.card import MarkRetainCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Equilibrium(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_block = 13
    upgrade_block = 16

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        for card in list(game_state.player.card_manager.get_pile("hand")):
            if card is self:
                continue
            add_action(MarkRetainCardAction(card))
