from actions.card import AddCardAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Alpha(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 1
    base_exhaust = True
    text_name = "Alpha"
    text_description = "Shuffle a Beta into your draw pile. Exhaust."

    def on_play(self, targets: List = []):
        from cards.watcher.beta import Beta

        add_action(AddCardAction(Beta(), dest_pile="draw_pile"))
