"""
Colorless Rare Skill card - Thinking Ahead
"""

from typing import List
from actions.base import Action
from actions.card import ChooseMoveCardAction, DrawCardsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class ThinkingAhead(Card):
    """Draw cards, put card on top of draw pile, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 0
    base_draw = 2
    base_exhaust = True
    upgrade_exhaust = False

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        return super().on_play(targets) + [ChooseMoveCardAction(src="hand", dst="draw_pile", amount=1)] # todo: pos=PilePosType.TOP
