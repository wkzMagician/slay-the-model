"""
Ironclad Rare Power card - Barricade
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Barricade(Card):
    """Block does not expire at the start of your turn"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 3
    upgrade_cost = 2

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Apply BarricadePower
        actions.append(ApplyPowerAction(power="BarricadePower", target=game_state.player, amount=0, duration=-1))

        return actions
