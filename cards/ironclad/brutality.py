"""
Ironclad Rare Power card - Brutality
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Brutality(Card):
    """At start of your turn, lose 1 HP and draw 1 card"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 0
    upgrade_innate = True

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Apply BrutalityPower
        actions.append(ApplyPowerAction(power="BrutalityPower", target=game_state.player, amount=0, duration=-1))

        return actions
