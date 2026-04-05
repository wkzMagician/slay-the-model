from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.master_reality import MasterRealityPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class MasterReality(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 1
    text_name = "Master Reality"
    text_description = "Whenever a card is created during combat, upgrade it."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(MasterRealityPower(owner=game_state_module.game_state.player), game_state_module.game_state.player))
