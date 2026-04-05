from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.nirvana import NirvanaPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Nirvana(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"block": 3}
    upgrade_magic = {"block": 4}
    text_name = "Nirvana"
    text_description = "Whenever you Scry, gain {magic.block} Block."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(NirvanaPower(amount=self.get_magic_value("block"), owner=game_state_module.game_state.player), game_state_module.game_state.player))
