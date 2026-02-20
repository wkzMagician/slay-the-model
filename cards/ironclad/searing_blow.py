"""
Ironclad Uncommon Attack card - Searing Blow
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class SearingBlow(Card):
    """Deal damage, can be upgraded any number of times"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_damage = 12
    base_damage_gain = 4
    upgrade_limit = 99  # Can be upgraded any number of times

    @property
    def damage(self) -> int:
        """Damage increases with each upgrade"""
        from engine.game_state import game_state
        
        damage = self.base_damage
        
        for level in range(1, self.upgrade_level + 1):
            damage += self.base_damage_gain + max(0, level - 2)

        return damage
