from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.like_water import LikeWaterPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class LikeWater(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"block": 5}
    upgrade_magic = {"block": 7}
    text_name = "Like Water"
    text_description = "At the end of your turn, if you are in Calm, gain {magic.block} Block."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(LikeWaterPower(amount=self.get_magic_value("block"), owner=game_state_module.game_state.player), game_state_module.game_state.player))
