from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Insight(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.SPECIAL
    base_cost = 0
    base_draw = 2
    upgrade_draw = 3
    base_retain = True
    base_exhaust = True
    text_name = "Insight"
    text_description = "Retain. Draw {draw} cards. Exhaust."
