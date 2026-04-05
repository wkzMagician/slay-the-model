from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.establishment import EstablishmentPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Establishment(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 1
    text_name = "Establishment"
    text_description = "At the end of your turn, reduce the cost of retained cards by 1."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(EstablishmentPower(owner=game_state_module.game_state.player), game_state_module.game_state.player))
