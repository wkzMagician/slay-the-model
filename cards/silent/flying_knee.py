"""Silent common attack card - Flying Knee."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.energized import EnergizedPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class FlyingKnee(Card):
    """Deal damage and gain energy next turn."""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 8

    upgrade_damage = 11

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(EnergizedPower(amount=1, owner=game_state.player), game_state.player)
        ])
