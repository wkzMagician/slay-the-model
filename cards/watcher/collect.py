from actions.combat_status import ApplyPowerAction
from cards.base import COST_X, Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.collect import CollectPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Collect(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = COST_X
    base_exhaust = True
    text_name = "Collect"
    text_description = "Put Miracle+ into your hand at the start of your next X turns. Exhaust."

    def on_play(self, targets: List = []):
        duration = self.get_effective_x() + (1 if self.upgrade_level > 0 else 0)
        add_action(ApplyPowerAction(CollectPower(duration=duration, owner=game_state_module.game_state.player), game_state_module.game_state.player))
