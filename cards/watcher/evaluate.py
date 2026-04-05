from actions.card import AddCardAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Evaluate(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.COMMON
    base_cost = 1
    base_block = 6
    upgrade_block = 10
    text_name = "Evaluate"
    text_description = "Gain {block} Block. Shuffle an Insight into your draw pile."

    def on_play(self, targets: List = []):
        from cards.watcher.insight import Insight

        super().on_play(targets)
        add_action(AddCardAction(Insight(), dest_pile="draw_pile"))
