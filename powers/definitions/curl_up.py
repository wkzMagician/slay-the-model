# -*- coding: utf-8 -*-
"""
CurlUpPower - Louse enemy ability
When taking damage, gains block equal to the amount.
"""
from powers.base import Power
from localization import LocalStr
from utils.registry import register


@register("power")
class CurlUpPower(Power):
    """
    Curl Up power for Louse enemies.
    When the enemy takes damage, it gains block equal to the curl_up amount.
    
    This power is triggered by the enemy's on_damage_taken method.
    """
    
    def __init__(self, amount: int = 4):
        super().__init__()
        self.amount = amount
        self.name = "Curl Up"
        self.power_type = "ability"
        self.localization_key = "powers.curl_up"
        
    def local(self, key: str, **kwargs) -> LocalStr:
        """Get localized string for this power
        
        Args:
            key: The localization key ('name' or 'description')
            **kwargs: Optional arguments (e.g., amount from combat.py)
        """
        if key == "name":
            return LocalStr(f"{self.localization_key}.name", default=self.name)
        elif key == "description":
            # Use passed amount or fall back to self.amount
            amount = kwargs.get('amount', self.amount)
            return LocalStr(f"{self.localization_key}.description", 
                          default=f"On damage, gains {amount} Block.",
                          amount=amount)
        return super().local(key)
