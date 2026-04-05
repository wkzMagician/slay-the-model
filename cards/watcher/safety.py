from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Safety(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.SPECIAL
    base_cost = 1
    base_block = 12
    upgrade_block = 16
    base_retain = True
    base_exhaust = True
    text_name = "Safety"
    text_description = "Retain. Gain {block} Block. Exhaust."
