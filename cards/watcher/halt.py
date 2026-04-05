from actions.combat import GainBlockAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType

@register("card")
class Halt(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.COMMON
    base_cost = 0
    base_block = 3
    upgrade_block = 4
    base_magic = {"wrath_block": 9}
    upgrade_magic = {"wrath_block": 14}
    text_name = "Halt"
    text_description = "Gain {block} Block. If you are in Wrath, gain {magic.wrath_block} more."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        if game_state_module.game_state.player.status_manager.status == StatusType.WRATH:
            add_action(GainBlockAction(self.get_magic_value("wrath_block"), target=game_state_module.game_state.player))
