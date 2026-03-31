"""Defect uncommon skill card - Reprogram."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.dexterity import DexterityPower
from powers.definitions.focus import FocusPower
from powers.definitions.strength import StrengthPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Reprogram(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_magic = {"focus_loss": 1, "gain": 1}
    upgrade_magic = {"focus_loss": 2, "gain": 2}

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        gain = self.get_magic_value("gain")
        add_actions([
            ApplyPowerAction(FocusPower(amount=-self.get_magic_value("focus_loss"), owner=game_state.player), game_state.player),
            ApplyPowerAction(StrengthPower(amount=gain, owner=game_state.player), game_state.player),
            ApplyPowerAction(DexterityPower(amount=gain, owner=game_state.player), game_state.player),
        ])
