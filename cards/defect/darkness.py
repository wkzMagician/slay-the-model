"""Defect uncommon skill card - Darkness."""

from typing import List

from actions.base import LambdaAction
from actions.orb import AddOrbAction, OrbPassiveAction
from cards.base import Card
from entities.creature import Creature
from orbs.dark import DarkOrb
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Darkness(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(AddOrbAction(DarkOrb()))
        if self.upgrade_level > 0 and game_state.player is not None:
            def _trigger_all_dark_orbs():
                if game_state.player is None:
                    return
                for orb in game_state.player.orb_manager.orbs:
                    if isinstance(orb, DarkOrb):
                        add_action(OrbPassiveAction(orb))

            add_action(LambdaAction(_trigger_all_dark_orbs))
