"""Defect rare attack card - Hyperbeam."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.focus import FocusPower
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Hyperbeam(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.RARE
    base_target_type = TargetType.ENEMY_ALL

    base_cost = 2
    base_damage = 26
    upgrade_damage = 34

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(FocusPower(amount=-3, owner=game_state.player), game_state.player))
