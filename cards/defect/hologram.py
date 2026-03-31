"""Defect uncommon skill card - Hologram."""

from typing import List

from actions.card import ChooseMoveCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Hologram(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_block = 3
    base_exhaust = True

    upgrade_block = 5
    upgrade_exhaust = False

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_action

        add_action(ChooseMoveCardAction(src="discard_pile", dst="hand", amount=1))
