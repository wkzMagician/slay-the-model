"""
Ironclad Common Skill card - Flex
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Flex(Card):
    """Gain Strength, lose it at end of turn"""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 0
    base_magic = {"temp_strength": 2}

    upgrade_magic = {"temp_strength": 4}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Gain temporary Strength
        strength_amount = self.get_magic_value("temp_strength")
        actions.extend([
            ApplyPowerAction(power="Strength", target=game_state.player, amount=strength_amount),
            ApplyPowerAction(power="StrengthDown", target=game_state.player, amount=strength_amount, duration=1)  # This power should handle the strength loss at end of turn
        ])
        return actions
