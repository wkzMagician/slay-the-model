"""Silent common skill card - Cloak And Dagger."""

from typing import List

from actions.card import AddCardAction
from cards.base import Card
from cards.colorless.shiv import Shiv
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class CloakAndDagger(Card):
    """Gain Block and add Shivs to your hand."""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_block = 6
    base_magic = {"shivs": 1}

    upgrade_block = 8
    upgrade_magic = {"shivs": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_actions

        add_actions([
            AddCardAction(card=Shiv(), dest_pile="hand")
            for _ in range(self.get_magic_value("shivs"))
        ])
