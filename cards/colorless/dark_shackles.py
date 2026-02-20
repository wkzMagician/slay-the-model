"""
Colorless Uncommon Skill card - Dark Shackles
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class DarkShackles(Card):
    """Enemy loses Strength this turn, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 0
    base_magic = {"strength_loss": 9}
    base_exhaust = True

    upgrade_magic = {"strength_loss": 15}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        actions = super().on_play(targets)

        # Enemy loses Strength this turn (temporary weakness)
        if targets:
            strength_loss = self.get_magic_value("strength_loss")
            # Apply Strength (negative value reduces strength)
            actions.append(ApplyPowerAction(
                power="Strength",
                target=target,
                amount=-strength_loss,
                duration=1  # Lasts only this turn
            ))

        return actions
