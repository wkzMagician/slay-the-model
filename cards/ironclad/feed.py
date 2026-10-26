"""
Ironclad Rare Attack card - Feed
"""
from cards.base import Card
from entities.creature import Creature
from utils.dynamic_values import get_magic_value
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Feed(Card):
    """Deal damage, if Fatal raise Max HP"""

    card_type = CardType.ATTACK
    rarity = RarityType.RARE

    base_cost = 1
    base_damage = 10
    base_exhaust = True

    upgrade_damage = 12
    
    base_magic = {"max_health_gain": 3, "max_hp": 3}
    upgrade_magic = {"max_health_gain": 4, "max_hp": 4}

    def on_fatal(self, damage: int, target: Creature, source=None, card: Card | None = None, damage_type: str = "direct"):
        """When this card kills an enemy, gain max HP"""
        from actions.combat import ModifyMaxHpAction

        if card is not self or target is None or getattr(target, "is_minion", False):
            return

        max_hp_gain = get_magic_value(
            self,
            "max_hp",
            get_magic_value(self, "max_health_gain"),
        )
        # FeedAction raises HP inside the damage action, before post-combat
        # queue cleanup. Queuing this reward would discard a final-kill gain.
        ModifyMaxHpAction(amount=max_hp_gain).execute()
        return
