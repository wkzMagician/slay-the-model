from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class WheelKick(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 15
    upgrade_damage = 20
    base_draw = 2
    text_name = "Wheel Kick"
    text_description = "Deal {damage} damage. Draw {draw} cards."
