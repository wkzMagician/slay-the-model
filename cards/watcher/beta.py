from actions.card import AddCardAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Beta(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.SPECIAL
    base_cost = 2
    base_exhaust = True
    text_name = "Beta"
    text_description = "Shuffle an Omega into your draw pile. Exhaust."

    def on_play(self, targets: List = []):
        from cards.watcher.omega import Omega

        add_action(AddCardAction(Omega(), dest_pile="draw_pile"))
