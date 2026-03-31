"""Defect rare skill card - Fission."""

from typing import List

from actions.card import DrawCardsAction
from actions.combat import GainEnergyAction
from actions.orb import EvokeAllOrbsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Fission(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 0
    base_exhaust = True

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        orb_count = len(game_state.player.orb_manager.orbs)
        actions = [GainEnergyAction(energy=orb_count), DrawCardsAction(count=orb_count)]
        if self.upgrade_level > 0:
            actions.insert(0, EvokeAllOrbsAction())
        else:
            game_state.player.orb_manager.clear_all()
        add_actions(actions)
