"""Defect common attack card - Rebound."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.rebound import ReboundPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Rebound(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 9
    upgrade_damage = 12

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(ReboundPower(owner=game_state.player), game_state.player))
