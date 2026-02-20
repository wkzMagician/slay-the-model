"""
Ironclad Uncommon Power card - Evolve
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Evolve(Card):
    """Whenever you draw a status card, draw 1/2"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Apply EvolvePower
        # The amount is handled by the power's on_card_draw hook
        actions.append(ApplyPowerAction(power="EvolvePower", target=game_state.player, amount=1, duration=-1))

        return actions
