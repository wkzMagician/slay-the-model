from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Miracle(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.SPECIAL
    base_cost = 0
    base_energy_gain = 1
    upgrade_energy_gain = 2
    base_exhaust = True
    text_name = "Miracle"
    text_description = "Gain {energy_gain} Energy. Exhaust."
