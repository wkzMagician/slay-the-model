from actions.combat_status import ApplyPowerAction
from cards.base import Card
from engine.runtime_api import add_action
from powers.definitions.omega import OmegaPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Omega(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.SPECIAL
    base_cost = 3
    base_exhaust = True
    text_name = "Omega"
    text_description = "At the end of your turn, deal 50 damage to ALL enemies."

    def on_play(self, targets: List = []):
        from engine.game_state import game_state

        player = game_state.player
        add_action(ApplyPowerAction(OmegaPower(amount=50, owner=player), player))
