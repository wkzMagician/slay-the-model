"""Defect common skill card - Recursion."""

from typing import List

from actions.orb import AddOrbAction, EvokeOrbAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Recursion(Card):
    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        if game_state.player is None or not game_state.player.orb_manager.orbs:
            return
        orb_cls = type(game_state.player.orb_manager.orbs[0])
        add_actions([EvokeOrbAction(index=0), AddOrbAction(orb_cls())])
