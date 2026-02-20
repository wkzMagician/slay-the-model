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

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state
        from actions.combat import ApplyPowerAction

        actions = super().on_play(target)

        # Apply Magnetism power
        actions.append(ApplyPowerAction(
            power="MagnetismPower",
            target=game_state.player,
            amount=1,
            duration=-1  # Permanent for this combat
        ))

        return actions
