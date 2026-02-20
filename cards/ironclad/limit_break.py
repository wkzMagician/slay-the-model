"""
Ironclad Rare Skill card - Limit Break
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class LimitBreak(Card):
    """Double your Strength for the combat"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 1
    base_exhaust = True
    
    upgrade_exhaust = False

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Double Strength
        strength_power = game_state.player.get_power("strength")
        if strength_power is not None:
            current_strength = strength_power.amount
            actions.append(ApplyPowerAction(target=game_state.player, power="strength", amount=current_strength))

        return actions
