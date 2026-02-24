"""
Colorless Uncommon Skill card - Forethought
"""

from typing import List
from actions.base import Action
from actions.card import ChooseMoveAndSetCostAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, PilePosType, RarityType


@register("card")
class Forethought(Card):
    """Put card(s) to bottom of draw pile, costs 0 until played.
    
    Base: Put 1 card from hand to bottom of draw pile, it costs 0 until played.
    Upgrade: Put any number of cards from hand to bottom of draw pile, 
             they cost 0 until played.
    """

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_magic = {"put_bottom": 1}

    upgrade_magic = {"put_bottom": -1}  # -1 means any number of cards

    def on_play(self, targets: List[Creature] = None) -> List[Action]:
        """Execute Forethought effect.
        
        Returns an action that lets player choose cards to move to bottom 
        of draw pile with temporary cost of 0.
        """
        targets = targets or []
        actions = super().on_play(targets)

        # Get the number of cards that can be selected
        put_bottom = self.get_magic_value("put_bottom")
        
        # Upgraded version allows any number of cards (-1)
        # Base version allows only 1 card
        if self.upgrade_level > 0:
            amount = -1  # Any number
            must_select = False  # Can choose 0 cards
        else:
            amount = 1  # Only 1 card
            must_select = True  # Must choose 1 card

        # Create the choose action that moves cards and sets temp cost to 0
        choose_action = ChooseMoveAndSetCostAction(
            src_pile="hand",
            dst_pile="draw_pile",
            amount=amount,
            temp_cost=0,
            position=PilePosType.BOTTOM,
            must_select=must_select
        )
        
        actions.append(choose_action)
        return actions