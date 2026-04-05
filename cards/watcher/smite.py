from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Smite(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.SPECIAL
    base_cost = 1
    base_damage = 12
    upgrade_damage = 16
    base_retain = True
    base_exhaust = True
    text_name = "Smite"
    text_description = "Retain. Deal {damage} damage. Exhaust."
