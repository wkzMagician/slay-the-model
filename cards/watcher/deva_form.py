from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class DevaForm(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 3
    text_name = "Deva Form"
    text_description = "At the start of your turn, gain Energy and increase this effect."

    def on_play(self, targets: List = []):
        from powers.definitions.deva import DevaPower

        add_action(ApplyPowerAction(DevaPower(duration=1, owner=game_state_module.game_state.player), game_state_module.game_state.player))
