from actions.watcher import GainMantraAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Worship(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_innate = False
    upgrade_innate = True
    text_name = "Worship"
    text_description = "Gain 5 Mantra."

    def on_play(self, targets: List = []):
        add_action(GainMantraAction(5))
