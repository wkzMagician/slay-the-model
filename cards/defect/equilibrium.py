"""Defect uncommon skill card - Equilibrium."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.equilibrium import EquilibriumPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Equilibrium(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_block = 13
    upgrade_block = 16
    base_magic = {"retain_turns": 1}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        turns = self.get_magic_value("retain_turns", 1)
        add_action(
            ApplyPowerAction(
                EquilibriumPower(amount=turns, duration=-1, owner=game_state.player),
                game_state.player,
            )
        )
