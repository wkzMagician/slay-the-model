from actions.card import DrawCardsAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType

@register("card")
class Sanctity(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 6
    upgrade_block = 9
    text_name = "Sanctity"
    text_description = "Gain {block} Block. If you are in Calm, draw 2 cards."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        if game_state_module.game_state.player.status_manager.status == StatusType.CALM:
            add_action(DrawCardsAction(2))
