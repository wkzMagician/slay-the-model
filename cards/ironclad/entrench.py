"""
Ironclad Uncommon Skill card - Entrench
"""

from typing import List
from actions.base import Action
from actions.combat import GainBlockAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Entrench(Card):
    """Double current block"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1

    upgrade_cost = 0

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Double current block
        current_block = game_state.player.block
        actions.append(GainBlockAction(block=current_block, target=game_state.player))

        return actions
