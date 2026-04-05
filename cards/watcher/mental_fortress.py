from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.mental_fortress import MentalFortressPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class MentalFortress(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"block": 4}
    upgrade_magic = {"block": 6}
    text_name = "Mental Fortress"
    text_description = "Whenever you change stances, gain {magic.block} Block."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(MentalFortressPower(amount=self.get_magic_value("block"), owner=game_state_module.game_state.player), game_state_module.game_state.player))
