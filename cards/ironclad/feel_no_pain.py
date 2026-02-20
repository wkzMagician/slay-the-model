"""
Ironclad Uncommon Power card - Feel No Pain
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class FeelNoPain(Card):
    """Whenever you exhaust one card, gain 3/4 Block"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"block_per_exhaust": 3}

    upgrade_magic = {"block_per_exhaust": 4}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Apply FeelNoPainPower
        block_per_exhaust = self.get_magic_value("block_per_exhaust")
        actions.append(ApplyPowerAction(power="FeelNoPainPower", target=game_state.player, amount=block_per_exhaust))

        return actions
