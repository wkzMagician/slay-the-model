from actions.card import DrawCardsAction
from actions.watcher import ChangeStanceAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType

@register("card")
class InnerPeace(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_draw = 3
    upgrade_draw = 4
    text_name = "Inner Peace"
    text_description = "Enter Calm. If you are already in Calm, draw {draw} cards."

    def on_play(self, targets: List = []):
        was_calm = game_state_module.game_state.player.status_manager.status == StatusType.CALM
        add_action(ChangeStanceAction(StatusType.CALM))
        if was_calm:
            add_action(DrawCardsAction(self.draw))
