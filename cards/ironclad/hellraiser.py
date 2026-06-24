"""
Ironclad Rare Power card - Hellraiser
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Hellraiser(Card):
    """Whenever you draw a card containing "Strike" it is played against a random enemy."""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 1
    # Power has no magic numbers, effect is handled by HellraiserPower

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        from engine.game_state import game_state

        super().on_play(targets)

        actions = []
        # Apply HellraiserPower
        actions.append(ApplyPowerAction(power="HellraiserPower", target=game_state.player, amount=1, duration=-1))

        add_actions(actions)
        return
