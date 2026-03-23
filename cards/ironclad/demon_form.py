"""
Ironclad Rare Power card - Demon Form
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DemonForm(Card):
    """At end of your turn, gain 2 Strength"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 3
    base_magic = {"strength_per_turn": 2, "strength": 2}

    upgrade_magic = {"strength_per_turn": 3, "strength": 3}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Apply DemonFormPower
        strength_per_turn = self.get_magic_value("strength_per_turn")
        actions.append(ApplyPowerAction(power="DemonFormPower", target=target, amount=strength_per_turn, duration=-1))

        return actions
