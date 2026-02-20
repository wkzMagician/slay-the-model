"""
Colorless Rare Power card - Magnetism
"""

from typing import List
from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from powers.base import Power
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Magnetism(Card):
    """Power: Add random colorless card at start of turn"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 2

    upgrade_cost = 1

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state
        from actions.combat import ApplyPowerAction

        actions = super().on_play(targets)

        # Apply Magnetism power
        actions.append(ApplyPowerAction(
            power="MagnetismPower",
            target=game_state.player,
            amount=1,
            duration=-1  # Permanent for this combat
        ))

        return actions
