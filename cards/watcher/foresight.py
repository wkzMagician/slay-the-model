from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.foresight import ForesightPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Foresight(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"scry": 3}
    upgrade_magic = {"scry": 4}
    text_name = "Foresight"
    text_description = "At the start of your turn, Scry {magic.scry}."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(ForesightPower(amount=self.get_magic_value("scry"), owner=game_state_module.game_state.player), game_state_module.game_state.player))
