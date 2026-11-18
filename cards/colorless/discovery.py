"""
Colorless Uncommon Skill card - Discovery
"""
from engine.runtime_api import add_actions
from typing import List
from actions.card import ChooseAddRandomCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Discovery(Card):
    """Choose 1 of 3 random cards, costs 0 this turn, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_exhaust = True

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        add_actions([
            ChooseAddRandomCardAction(
                total=3,
                must_select=True,
                cost_until_end_of_turn=0 if self.upgrade_level > 0 else None,
            )
        ])
