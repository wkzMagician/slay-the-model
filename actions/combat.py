from actions.base import Action
from utils.registry import register

@register("action")
class ModifyMaxHpAction(Action):
    """Modify player's max HP
    
    Required:
        amount (int): HP change amount
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "amount": int,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        amount = self.kwargs.get('amount', 0)
        if game_state.player:
            game_state.player.max_hp += amount
            from localization import t
            print(t("ui.max_hp_changed", default=f"Max HP changed by {amount}!"))
            
@register("action")
class LoseHpAction(Action):
    """Modify player's HP
    
    Required:
        amount (int): HP change amount
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "amount": int,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        amount = self.kwargs.get('amount', 0)
        if game_state.player:
            game_state.player.hp -= amount