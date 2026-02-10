"""
Ironclad Uncommon Skill card - Dual Wield
"""

from typing import List
from actions.base import Action
from actions.card import AddCardAction, ChooseCopyCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DualWield(Card):
    """Choose a card in hand and add a copy"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1

    upgrade_cost = 0

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Choose a card in hand and add a copy
        if game_state.player.card_manager.get_pile("hand"):
            actions.append(ChooseCopyCardAction(pile="hand", copies=1))

        return actions
