from actions.card_choice import ChooseAddRandomCardAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class ForeignInfluence(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 0
    base_exhaust = True
    text_name = "Foreign Influence"
    text_description = "Choose 1 of 3 attacks from any color to add to your hand. It costs 0 this turn. Exhaust."

    def on_play(self, targets: List = []):
        add_action(
            ChooseAddRandomCardAction(
                total=3,
                card_type=CardType.ATTACK,
                cost_until_end_of_turn=0 if self.upgrade_level > 0 else None,
            )
        )
