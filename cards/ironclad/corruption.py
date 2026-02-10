"""
Ironclad Rare Power card - Corruption
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Corruption(Card):
    """Skills cost 0 energy"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 3
    upgrade_cost = 2

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Apply CorruptionPower
        actions.append(ApplyPowerAction(power="CorruptionPower", target=game_state.player, amount=0, duration=0))

        return actions
