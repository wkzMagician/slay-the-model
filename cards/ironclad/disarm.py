"""
Ironclad Uncommon Skill card - Disarm
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Disarm(Card):
    """Apply Strength to enemy"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_magic = {"strength_debuff": 2}

    upgrade_magic = {"strength_debuff": 3}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        actions = super().on_play(targets)

        # Apply Strength debuff to target
        if targets:
            strength_amount = self.get_magic_value("strength_debuff")
            actions.append(ApplyPowerAction(target=target, power="strength", amount=-strength_amount))

        return actions
