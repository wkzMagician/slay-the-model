"""
Colorless Special Skill card - JAX
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction, LoseHPAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class JAX(Card):
    """Lose HP, gain Strength"""

    card_type = CardType.SKILL
    rarity = RarityType.SPECIAL

    base_cost = 0
    base_heal = -3
    base_magic = {"strength": 2}

    upgrade_magic = {"strength": 3}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Gain Strength
        strength_amount = self.get_magic_value("strength")
        actions.append(ApplyPowerAction(
            power="Strength",
            target=game_state.player,
            amount=strength_amount
        ))

        return actions
