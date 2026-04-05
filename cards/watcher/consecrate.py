from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Consecrate(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_ALL
    base_cost = 0
    base_damage = 5
    upgrade_damage = 8
    text_name = "Consecrate"
    text_description = "Deal {damage} damage to ALL enemies."
