from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_actions
from powers.definitions.dexterity import DexterityPower
from powers.definitions.fasting import FastingPower
from powers.definitions.strength import StrengthPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Fasting(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_magic = {"stat": 3}
    upgrade_magic = {"stat": 4}
    text_name = "Fasting"
    text_description = "Gain {magic.stat} Strength and Dexterity. Gain 1 less Energy at the start of each turn."

    def on_play(self, targets: List = []):
        amount = self.get_magic_value("stat")
        player = game_state_module.game_state.player
        add_actions(
            [
                ApplyPowerAction(StrengthPower(amount=amount, owner=player), player),
                ApplyPowerAction(DexterityPower(amount=amount, owner=player), player),
                ApplyPowerAction(FastingPower(owner=player), player),
            ]
        )
