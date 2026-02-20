"""
Colorless Uncommon Skill card - Forethought
"""

from typing import List
from actions.base import Action
from actions.card import ChooseMoveCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, PilePosType, RarityType


@register("card")
class Forethought(Card):
    """Put card(s) to bottom of draw pile, costs 0 until played"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_magic = {"put_bottom": 1}

    upgrade_magic = {"put_bottom": -1}  # -1 means any number of cards

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        actions = super().on_play(targets)

        put_bottom = self.get_magic_value("put_bottom")
        temp_cost = 0

        if self.upgrade_level > 0:
            # Upgraded: Put any number of cards to bottom
            # We'll use max_select to allow multiple selections
            put_bottom = -1  # Allow any number
        else:
            # Base: Put 1 card to bottom
            put_bottom = 1

        # Choose cards to move to bottom of draw pile
        # todo: 新写一个ChooseCardAction，它的参数传入一个callback_actions (List[Actions])，
        # 它能把选中的List[Card]中的每一个 card, 作为参数传入 callback_actions，再把 callback_actions 返回
        # 在这一个例子中，callback_actions就是MoveCardAction

        return actions
