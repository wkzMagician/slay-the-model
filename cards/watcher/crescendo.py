from actions.watcher import ChangeStanceAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType

@register("card")
class Crescendo(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.COMMON
    base_cost = 1
    upgrade_cost = 0
    base_retain = True
    base_exhaust = True
    text_name = "Crescendo"
    text_description = "Retain. Enter Wrath. Exhaust."

    def on_play(self, targets: List = []):
        add_action(ChangeStanceAction(StatusType.WRATH))
