"""
Ironclad Uncommon Power card - Inflame
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Inflame(Card):
    """Gain 2 Strength"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"strength": 2}

    upgrade_magic = {"strength": 3}
    
    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Gain Strength (permanent)
        strength_amount = self.get_magic_value("strength")
        actions.extend([
            ApplyPowerAction(power="Strength", target=game_state.player, amount=strength_amount),
        ])
        return actions

