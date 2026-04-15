"""
Colorless Special Attack card - Ritual Dagger
"""
from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class RitualDagger(Card):
    """Deal damage, permanently increase damage on kill, Exhaust"""

    card_type = CardType.ATTACK
    rarity = RarityType.SPECIAL
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_damage = 15
    base_magic = {"fatal_bonus": 3, "damage_increase": 3}
    base_exhaust = True

    upgrade_magic = {"fatal_bonus": 5, "damage_increase": 5}

    def on_fatal(self, damage: int, target=None, source=None, card=None, damage_type: str = "direct"):
        """If this kills enemy, permanently increase this Card's damage"""
        if card is not self or target is None:
            return

        fatal_bonus = self.get_magic_value(
            "damage_increase",
            self.get_magic_value("fatal_bonus"),
        )
        # Permanently increase this card instance's damage
        self._damage += fatal_bonus