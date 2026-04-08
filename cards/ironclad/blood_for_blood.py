"""
Ironclad Uncommon Attack card - Blood for Blood
"""

from typing import List, Optional
from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BloodForBlood(Card):
    """Deal damage, costs less for each HP lost this combat"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 4
    base_damage = 18

    upgrade_cost = 3
    upgrade_damage = 22

    def on_damage_taken(
        self,
        damage: int,
        source: Optional[Creature] = None,
        player: Optional[Creature] = None,
    ):
        """Track HP taken to reduce card cost"""
        from engine.game_state import game_state

        if player is not game_state.player:
            return
        # Reduce cost by 1 each time damage is taken (minimum 0)
        self._cost = max(0, self._cost - 1)
        return

    def on_lose_hp(self, amount: int, source=None, card=None):
        """HP loss also reduces the card's cost this combat."""
        if amount > 0:
            self._cost = max(0, self._cost - 1)
        return

    def apply_upgrade(self):
        current_cost = self._cost
        super().apply_upgrade()
        if current_cost < self.base_cost:
            self._cost = max(0, current_cost - 1)
