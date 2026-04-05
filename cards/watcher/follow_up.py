from actions.combat import GainEnergyAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class FollowUp(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 7
    upgrade_damage = 11
    text_name = "Follow-Up"
    text_description = "Deal {damage} damage. If the previous card played this turn was an Attack, gain 1 Energy."

    def on_play(self, targets: List = []):
        player = game_state_module.game_state.player
        discard = [] if player is None else player.card_manager.get_pile("discard_pile")
        previous = discard[-1] if discard else None
        super().on_play(targets)
        if previous is not None and getattr(previous, "card_type", None) == CardType.ATTACK:
            add_action(GainEnergyAction(1))
