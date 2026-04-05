from cards.base import Card
import random
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Ragnarok(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.RARE
    base_cost = 3
    base_damage = 5
    upgrade_damage = 6
    base_attack_times = 5
    upgrade_attack_times = 6
    target_type = TargetType.ENEMY_RANDOM
    text_name = "Ragnarok"
    text_description = "Deal {damage} damage to a random enemy {attack_times} times."
