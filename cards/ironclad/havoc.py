"""
Ironclad Common Skill card - Havoc
"""
from engine.runtime_api import add_action

from typing import List
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Havoc(Card):
    """Play top card of draw pile and exhaust it"""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1

    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        from actions.autoplay import PlayTopCardAction
        add_action(PlayTopCardAction(exhaust=True))
