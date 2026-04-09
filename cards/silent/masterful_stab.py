"""Silent uncommon attack card - Masterful Stab."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class MasterfulStab(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_damage = 12

    upgrade_damage = 16

    def on_any_hp_lost(self, amount: int, source=None, card=None):
        if amount > 0:
            self._cost += 1
