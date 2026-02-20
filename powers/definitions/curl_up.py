# -*- coding: utf-8 -*-
"""
CurlUpPower - Louse enemy ability
When taking damage, gains block equal to the amount.
"""
from powers.base import Power
from localization import LocalStr
from utils.registry import register
from actions.combat import RemovePowerAction


@register("power")
class CurlUpPower(Power):
    """
    Curl Up power for Louse enemies.
    When the enemy takes damage, it gains block equal to the curl_up amount.
    
    This power is triggered by the enemy's on_damage_taken method.
    """
    
    def __init__(self, amount: int = 4, owner=None):
        super().__init__()
        self.amount = amount
        self.owner = owner
        self.name = "Curl Up"
        self.power_type = "ability"
        self.localization_key = "powers.curl_up"
        self.triggered = False
        
    def on_damage_taken(self, damage: int, source=None, card=None, player=None, damage_type="direct"):
        """
        Called when owner takes damage.
        Gains block equal to amount, then removes.
        
        Args:
            damage: Amount of damage taken itself
            source: Source of the damage (optional)
            card: Card that caused damage (optional)
            player: Player taking damage (optional)
            damage_type: Type of damage (optional)
            
        Returns:
            List of actions (RemovePowerAction to remove this power)
        """
        if not self.triggered and damage > 0:
            self.triggered = True
            if self.owner:
                self.owner.gain_block(self.amount)
            # Return RemovePowerAction to remove this power immediately
            return [RemovePowerAction(power="Curl Up", target=self.owner)]
        return []
        
    def local(self, field: str, **kwargs) -> LocalStr:
        """Get localized string for this power
        
        Args:
            field: The localization field ('name' or 'description')
            **kwargs: Optional arguments (e.g., amount from combat.py)
        """
        if field == "name":
            return LocalStr(f"{self.localization_key}.name", default=self.name)
        elif field == "description":
            # Use passed amount or fall back to self.amount
            amount = kwargs.get('amount', self.amount)
            return LocalStr(f"{self.localization_key}.description", 
                          default=f"On damage, gains {amount} Block.",
                          amount=amount)
        return super().local(field)
