"""Silent uncommon power card - Infinite Blades."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.infinite_blades import InfiniteBladesPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class InfiniteBlades(Card):
    """Add a Shiv to your hand at the start of each turn."""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(InfiniteBladesPower(amount=1, owner=game_state.player), game_state.player)
        ])
