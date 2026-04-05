from actions.card import DrawCardsAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Scrawl(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 1
    upgrade_cost = 0
    base_exhaust = True
    text_name = "Scrawl"
    text_description = "Draw cards until your hand is full. Exhaust."

    def on_play(self, targets: List = []):
        player = game_state_module.game_state.player
        draw_needed = max(0, player.card_manager.HAND_LIMIT - len(player.card_manager.get_pile("hand")))
        if draw_needed:
            add_action(DrawCardsAction(draw_needed))
