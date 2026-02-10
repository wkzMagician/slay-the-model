"""
Ironclad Uncommon Power card - Dark Embrace
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DarkEmbrace(Card):
    """Whenever a card is Exhausted, draw 1"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 2
    upgrade_cost = 1

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Apply DarkEmbracePower
        actions.append(ApplyPowerAction(power="DarkEmbracePower", target=game_state.player, amount=0, duration=0))

        return actions
