# -*- coding: utf-8 -*-
"""Thievery power - steals gold when attacking."""

from typing import List, Any, TYPE_CHECKING
from powers.base import Power
from utils.registry import register

if TYPE_CHECKING:
    from actions.base import Action


@register("power")
class ThieveryPower(Power):
    """Thievery - Steals X Gold whenever it attacks.
    
    Stolen gold is returned if this enemy is killed.
    """
    
    localization_prefix = "powers"
    stackable = True
    is_buff = True
    
    def __init__(self, amount: int = 15, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.stolen_gold = 0  # Track how much gold was stolen
    
    def on_attack(self, target: Any = None, source: Any = None, 
                   card: Any = None) -> List['Action']:
        """Steal gold when attacking the player.
        
        Triggered on attack action, regardless of whether damage is dealt.
        This matches the game behavior where Thievery steals gold even if
        the attack is blocked.
        
        Args:
            target: Target of the attack (player)
            source: Source of the attack
            card: Card being played
            
        Returns:
            Empty list (no actions from stealing)
        """
        from engine.game_state import game_state
        
        # Only steal from player
        if not target or target != game_state.player:
            return []
        
        # Calculate gold to steal
        gold_to_steal = min(self.amount, game_state.player.gold)
        
        if gold_to_steal > 0:
            game_state.player.gold -= gold_to_steal
            self.stolen_gold += gold_to_steal
            from localization import t
            owner_name = getattr(self.owner, 'name', 'Enemy') if self.owner else 'Enemy'
            print(t("combat.thievery_steal", default=f"{owner_name} stole {gold_to_steal} gold!", 
                    enemy=owner_name, amount=gold_to_steal))
        
        return []
    
    def on_remove(self) -> List['Action']:
        """Return stolen gold when the power is removed (enemy dies).
        
        Returns:
            Empty list (no actions)
        """
        from engine.game_state import game_state
        
        if self.stolen_gold > 0 and game_state.player:
            game_state.player.gold += self.stolen_gold
            from localization import t
            print(t("combat.thievery_return", default=f"Recovered {self.stolen_gold} stolen gold!", 
                    amount=self.stolen_gold))
        
        return []