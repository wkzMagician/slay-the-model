"""
Ironclad Common Attack card - Clothesline
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Clothesline(Card):
    """Deal damage and apply Weak"""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 2
    base_damage = 12
    base_magic = {"weak": 2}

    upgrade_damage = 14
    upgrade_magic = {"weak": 3}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)
        weak_amount = self.get_magic_value("weak")

        # Apply weak debuff to target
        if targets:
            actions.append(ApplyPowerAction(target=target, power="weak", amount=weak_amount))

        return actions
