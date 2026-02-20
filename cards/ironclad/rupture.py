"""
Ironclad Uncommon Power card - Rupture
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Rupture(Card):
    """Whenever you lose HP from a card, gain 1/2 Strength"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"strength_gain": 1}

    upgrade_magic = {"strength_gain": 2}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Apply RupturePower
        strength_gain = self.get_magic_value("strength_gain")
        actions.append(ApplyPowerAction(power="RupturePower", target=game_state.player, amount=strength_gain))

        return actions
