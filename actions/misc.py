"""
Miscellaneous actions
"""
from actions.base import Action
from utils.registry import register

@register("action")
class MoveToPositionAction(Action):
    """Move to a new position
    
    Required:
        position (str): Target position
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "position": str,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        position = self.kwargs.get('position')
        if position:
            game_state.move_to_position(position)
        game_state.current_floor += 1

@register("action")
class GenerateMapAction(Action):
    """Generate a new map and update global state
    
    Required:
        None
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        game_state.generate_initial_map()
        from localization import t
        print(t("ui.map_generated", default="Map generated for new act!"))

@register("action")
class StartEventAction(Action):
    """Action to start an event - inserted to queue head
    
    Required:
        None
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        current_event = game_state.current_event
        if current_event:
            current_event.start_event()
            
@register("action")
class EndEventAction(Action):
    """Action to end an event - inserted to queue head
    
    Required:
        None
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        current_event = game_state.current_event
        if current_event:
            current_event.end_event()

@register("action")
class AddRelicAction(Action):
    """Add a specific relic to player
    
    Required:
        relic (str): Relic name
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "relic": str,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        relic_name = self.kwargs.get('relic')
        if relic_name and game_state.player:
            from relics.base import create_relic
            relic = create_relic(relic_name)
            if relic:
                game_state.player.relics.append(relic)
                from localization import t
                print(t("ui.received_relic", default=f"Received relic: {relic.name}!", name=relic.name))
                return relic
            
@register("action")
class AddRandomRelicAction(Action):
    """Add a random relic to player
    
    Required:
        rarity (str): Relic rarity
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "rarity": str,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        rarity = self.kwargs.get('rarity')
        if rarity and game_state.player:
            from relics.base import create_random_relic
            relic = create_random_relic(rarity)
            if relic:
                game_state.player.relics.append(relic)
                from localization import t
                print(t("ui.received_relic", default=f"Received relic: {relic.name}!", name=relic.name))
                return relic
            
@register("action")
class LoseRelicAction(Action):
    """Lose a specific relic from player
    
    Required:
        relic (str): Relic name
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "relic": str,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        relic_name = self.kwargs.get('relic')
        if relic_name and game_state.player:
            game_state.player.relics = [r for r in game_state.player.relics if r.name != relic_name]
            
@register("action")
class AddGoldAction(Action):
    """Add gold to player
    
    Required:
        amount (int): Amount of gold to add
        
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
            game_state.player.gold += amount
            
@register("action")
class LoseGoldAction(Action):
    """Lose gold from player
    
    Required:
        amount (int): Amount of gold to lose
        
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
            game_state.player.gold -= amount
            
@register("action")
class AddRandomPotionAction(Action):
    """Add a random potion to player
    
    Required:
        None
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        if game_state.player:
            from potions.base import create_random_potion
            potion = create_random_potion()
            if potion:
                game_state.player.potions.append(potion)
                from localization import t
                print(t("ui.received_potion", default=f"Received potion: {potion.name}!", name=potion.name))
                return potion