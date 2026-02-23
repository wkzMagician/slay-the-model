"""Time Warp power for Time Eater boss.

Whenever the player plays a certain number of cards (x12), 
ends their turn and the owner gains 1 Strength.
"""
from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction, EndTurnAction
from powers.base import Power, StackType
from utils.registry import register
from tui.print_utils import tui_print
from localization import LocalStr


@register("power")
class TimeWarpPower(Power):
    """Time Warp - Time Eater's signature power.
    
    Whenever the player plays 12 cards, ends their turn 
    and the owner gains 1 Strength.
    """
    
    name = "Time Warp"
    description = "Whenever you play 12 cards, end your turn and gain 1 Strength."
    stack_type = StackType.INTENSITY
    is_buff = True
    localization_prefix = "powers"
    localizable_fields = ("name", "description")
    
    # Card threshold to trigger effect
    CARD_THRESHOLD = 12
    
    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        """
        Args:
            amount: Current card counter (starts at 0)
            duration: Always permanent (-1)
            owner: The enemy that has this power (Time Eater)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.card_counter = amount  # Cards played since last trigger
    
    def on_card_play(self, card, player, entities) -> List[Action]:
        """Called when a card is played.
        
        Increments counter and triggers effect when threshold is reached.
        
        Args:
            card: The card that was played
            player: The player who played the card
            entities: List of enemies in combat
            
        Returns:
            List of actions to execute (EndTurn + GainStrength when triggered)
        """
        from localization import t
        
        self.card_counter += 1
        
        # Print counter progress
        tui_print(t("powers.time_warp_counter", default=f"Time Warp: {self.card_counter}/{self.CARD_THRESHOLD}"))
        
        if self.card_counter >= self.CARD_THRESHOLD:
            # Reset counter
            self.card_counter = 0
            
            # Print trigger message
            tui_print(t("powers.time_warp_trigger", default="Time Warp triggers! Turn ended and Time Eater gains Strength!"))
            
            # Return actions: end turn and gain strength
            actions = []
            
            # End player turn using EndTurnAction
            actions.append(EndTurnAction())
            
            # Time Eater gains 1 Strength
            if self.owner:
                from powers.definitions.strength import StrengthPower
                actions.append(ApplyPowerAction(
                    StrengthPower(amount=1, owner=self.owner),
                    self.owner
                ))
            
            return actions
        
        return []
    
    @property
    def counter(self) -> int:
        """Current card counter."""
        return self.card_counter
    
    def info(self) -> str:
        """Get power info string."""
        return f"{self.local('name')} ({self.card_counter}/{self.CARD_THRESHOLD})"