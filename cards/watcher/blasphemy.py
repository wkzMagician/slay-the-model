from actions.combat_status import ApplyPowerAction
from actions.watcher import ChangeStanceAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_actions
from powers.definitions.blasphemer import BlasphemerPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType

@register("card")
class Blasphemy(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 1
    base_exhaust = True
    text_name = "Blasphemy"
    text_description = "Enter Divinity. Die next turn. Exhaust."

    def on_play(self, targets: List = []):
        player = game_state_module.game_state.player
        add_actions([ChangeStanceAction(StatusType.DIVINITY), ApplyPowerAction(BlasphemerPower(owner=player), player)])
