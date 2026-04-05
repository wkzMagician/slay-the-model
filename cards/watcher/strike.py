from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Strike(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.STARTER
    base_cost = 1
    base_damage = 6
    upgrade_damage = 9
    text_name = "Strike"
    text_description = "Deal {damage} damage."
