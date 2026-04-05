from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.rushdown import RushdownPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Rushdown(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"draw": 2}
    text_name = "Rushdown"
    text_description = "Whenever you enter Wrath, draw {magic.draw} cards."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(RushdownPower(amount=self.get_magic_value("draw"), owner=game_state_module.game_state.player), game_state_module.game_state.player))
