"""
Colorless Uncommon Skill card - Blind
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Blind(Card):
    """Apply Weak to enemy/all enemies"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    base_target_type = TargetType.ENEMY_SELECT
    upgrade_target_type = TargetType.ENEMY_ALL

    base_cost = 0

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Apply Weak to target(s)
        weak_amount = 2

        if self.upgrade_level > 0:
            # Upgraded: Apply to ALL enemies
            assert game_state.current_combat is not None
            for enemy in game_state.current_combat.enemies:
                actions.append(ApplyPowerAction(
                    power="Weak",
                    target=enemy,
                    amount=weak_amount
                ))
        else:
            # Base: Apply to single target
            if targets:
                actions.append(ApplyPowerAction(
                    power="Weak",
                    target=target,
                    amount=weak_amount
                ))

        return actions
