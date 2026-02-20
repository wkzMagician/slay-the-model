"""
Ironclad Common Attack card - Headbutt
"""

from typing import List
from actions.base import Action
from actions.card import ChooseMoveCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Headbutt(Card):
    """Deal damage and put card from discard on top of draw pile"""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 9

    upgrade_damage = 12

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        return super().on_play(targets) + [ChooseMoveCardAction(src="discard_pile", dst="draw_pile", amount=1)]
