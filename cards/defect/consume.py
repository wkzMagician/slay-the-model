"""Defect uncommon skill card - Consume."""

from typing import List

from actions.combat import ApplyPowerAction
from actions.orb import IncreaseOrbSlotsAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.focus import FocusPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Consume(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_magic = {"focus": 2}
    upgrade_magic = {"focus": 3}

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(FocusPower(amount=self.get_magic_value("focus"), owner=game_state.player), game_state.player),
            IncreaseOrbSlotsAction(amount=-1),
        ])
