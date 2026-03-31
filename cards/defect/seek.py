"""Defect rare skill card - Seek."""

from typing import List

from actions.card import ChooseMoveCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Seek(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 0
    base_exhaust = True
    base_magic = {"cards": 1}
    upgrade_magic = {"cards": 2}

    def on_play(self, targets: List[Creature] = []):
        from engine.runtime_api import add_action

        add_action(ChooseMoveCardAction(src="draw_pile", dst="hand", amount=self.get_magic_value("cards")))
