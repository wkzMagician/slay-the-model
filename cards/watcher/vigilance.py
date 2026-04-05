from actions.watcher import ChangeStanceAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType

@register("card")
class Vigilance(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.STARTER
    base_cost = 2
    base_block = 8
    upgrade_block = 12
    text_name = "Vigilance"
    text_description = "Gain {block} Block. Enter Calm."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.CALM))
