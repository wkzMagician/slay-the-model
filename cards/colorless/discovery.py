"""
Colorless Uncommon Skill card - Discovery
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action
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
    upgrade_exhaust = False

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        actions = []
        # Choose 1 of 3 random cards
        actions.append(ChooseAddRandomCardAction(
            total=3,
            namespace="colorless",
            cost_until_end_of_turn=0  # Cards cost 0 this turn
        ))

        from engine.game_state import game_state

        add_actions(actions)

        return
