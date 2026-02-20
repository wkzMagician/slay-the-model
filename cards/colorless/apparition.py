"""
Colorless Special Skill card - Apparition
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Apparition(Card):
    """Gain Intangible, Ethereal, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.SPECIAL

    base_cost = 1
    base_ethereal = True
    base_exhaust = True

    upgrade_ethereal = False  # Upgraded version removes Ethereal

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Gain Intangible
        intangible_amount = 1
        actions.append(ApplyPowerAction(
            power="Intangible",
            target=game_state.player,
            amount=intangible_amount
        ))

        return actions
