from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class ThroughViolence(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.SPECIAL
    base_cost = 0
    base_damage = 20
    upgrade_damage = 30
    base_retain = True
    base_exhaust = True
    text_name = "Through Violence"
    text_description = "Retain. Deal {damage} damage. Exhaust."
