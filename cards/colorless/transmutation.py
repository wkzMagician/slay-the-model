"""
Colorless Rare Skill card - Transmutation
"""

from typing import List
from actions.base import Action
from actions.card import AddRandomCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Transmutation(Card):
    """Add X random colorless cards, cost X energy, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = -1  # COST_X
    base_exhaust = True

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Get X value (energy spent)
        x_value = self.cost  # This will be the actual energy spent

        # Add X random colorless cards
        use_upgraded = self.upgrade_level > 0

        for _ in range(x_value):
            actions.append(AddRandomCardAction(
                pile="hand",
                namespace="colorless",
                temp_cost=0,  # Cost 0 this turn
                upgrade=use_upgraded  # Add upgrade parameter
            ))

        return actions
