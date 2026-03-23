"""
Ironclad Rare Attack card - Feed
"""

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

    upgrade_damage = 12
    
    base_magic = {"max_health_gain": 3, "max_hp": 3}
    upgrade_magic = {"max_health_gain": 4, "max_hp": 4}

    def on_fatal(self, damage: int, target: Creature, card: Card, damage_type: str) -> List[Action]:
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
        actions.append(ModifyMaxHpAction(
            target=game_state.player,
            amount=max_hp_gain
        ))
        return actions
