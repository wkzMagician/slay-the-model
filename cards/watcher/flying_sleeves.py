from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class FlyingSleeves(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 4
    upgrade_damage = 6
    base_attack_times = 2
    base_retain = True
    text_name = "Flying Sleeves"
    text_description = "Retain. Deal {damage} damage {attack_times} times."
