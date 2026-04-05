from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Defend(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.STARTER
    base_cost = 1
    base_block = 5
    upgrade_block = 8
    text_name = "Defend"
    text_description = "Gain {block} Block."
