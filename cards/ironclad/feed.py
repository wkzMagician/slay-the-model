"""
Ironclad Rare Attack card - Feed
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action
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
        from engine.game_state import game_state
        from actions.combat import ModifyMaxHpAction

        actions = []
        # Gain max HP on fatal kill
        max_hp_gain = get_magic_value(
            self,
            "max_hp",
            get_magic_value(self, "max_health_gain"),
        )
        actions.append(ModifyMaxHpAction(amount=max_hp_gain))
        from engine.game_state import game_state
        add_actions(actions)
        return
