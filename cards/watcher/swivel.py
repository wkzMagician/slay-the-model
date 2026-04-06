from actions.combat_status import ApplyPowerAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from powers.definitions.swivel import SwivelPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Swivel(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_block = 8
    upgrade_block = 11
    text_name = "Swivel"
    text_description = "Gain {block} Block. Your next Attack this turn costs 0."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        player = game_state_module.game_state.player
        tracked_costs = {}
        for card in list(player.card_manager.get_pile("hand")):
            if getattr(card, "card_type", None) != CardType.ATTACK:
                continue
            tracked_costs[card] = card.cost_until_end_of_turn
            card.cost_until_end_of_turn = 0
        add_action(ApplyPowerAction(SwivelPower(tracked_costs=tracked_costs, owner=player), player))
