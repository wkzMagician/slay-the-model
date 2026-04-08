"""
Ironclad Uncommon Skill card - Entrench
"""
from engine.runtime_api import add_action, add_actions

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

    base_cost = 2

    upgrade_cost = 1

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        from engine.game_state import game_state

        super().on_play(targets)

        actions = []
        # Double current block
        current_block = game_state.player.block
        actions.append(GainBlockAction(block=current_block, target=game_state.player))

        from engine.game_state import game_state

        add_actions(actions)

        return
