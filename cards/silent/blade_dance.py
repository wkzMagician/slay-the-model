"""Silent common skill card - Blade Dance."""

from typing import List

from actions.card import AddCardAction
from cards.base import Card
from cards.colorless.shiv import Shiv
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BladeDance(Card):
    """Add Shivs to your hand."""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_magic = {"shivs": 3}
    upgrade_magic = {"shivs": 4}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_actions

        add_actions([
            AddCardAction(card=Shiv(), dest_pile="hand")
            for _ in range(self.get_magic_value("shivs"))
        ])
