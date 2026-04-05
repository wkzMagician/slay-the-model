from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Protect(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.COMMON
    base_cost = 2
    base_block = 12
    upgrade_block = 16
    base_retain = True
    text_name = "Protect"
    text_description = "Retain. Gain {block} Block."
