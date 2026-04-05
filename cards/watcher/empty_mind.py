from actions.card import DrawCardsAction
from actions.watcher import ChangeStanceAction
from cards.base import Card
from engine.runtime_api import add_actions
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType

@register("card")
class EmptyMind(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_draw = 2
    upgrade_draw = 3
    text_name = "Empty Mind"
    text_description = "Exit your stance. Draw {draw} cards."

    def on_play(self, targets: List = []):
        add_actions([ChangeStanceAction(StatusType.NEUTRAL), DrawCardsAction(self.draw)])
