"""Defect uncommon skill card - Overclock."""

from typing import List

from actions.card import DrawCardsAction
from actions.card_lifecycle import AddCardAction
from cards.base import Card
from cards.colorless.burn import Burn
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, PilePosType, RarityType


@register("card")
class Overclock(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_draw = 2
    upgrade_draw = 3

    def on_play(self, targets: List[Creature] = []):
        from engine.runtime_api import add_actions

        add_actions([
            DrawCardsAction(count=self.draw),
            AddCardAction(card=Burn(), dest_pile="discard_pile", position=PilePosType.TOP),
        ])
