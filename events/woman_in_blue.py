"""
Event 5 - The Woman in Blue
"""
from utils.result_types import BaseResult
from events.base_event import Event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import LoseGoldAction, AddRandomPotionAction
from actions.combat import LoseHPAction
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option


@register_event(
    event_id="woman_in_blue",
    acts='shared',
    weight=100
)
class WomanInBlueEvent(Event):
    """
    The Woman in Blue - Buy potions
    
    [Buy 1 Potion] Lose 20 Gold. Obtain a random potion.
    [Buy 2 Potions] Lose 30 Gold. Obtain 2 random potions.
    [Buy 3 Potions] Lose 40 Gold. Obtain 3 random potions.
    [Leave] Lose HP equal to 5% of Max HP.
    """
    
    def trigger(self) -> 'BaseResult':
        """Trigger woman in blue encounter"""
        from utils.result_types import MultipleActionsResult
        from engine.game_state import game_state
        
        # Collect all actions
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key="events.woman_in_blue.description"
        ))
        
        # Build options
        options = []
        
        # Option 1: Buy 1 Potion - 20 Gold
        if game_state.player.gold >= 20:
            options.append(Option(
                name=LocalStr("events.woman_in_blue.option1"),
                actions=[
                    LoseGoldAction(amount=20),
                    AddRandomPotionAction(character=game_state.player.character),
                ]
            ))
        
        # Option 2: Buy 2 Potions - 30 Gold
        if game_state.player.gold >= 30:
            options.append(Option(
                name=LocalStr("events.woman_in_blue.option2"),
                actions=[
                    LoseGoldAction(amount=30),
                    AddRandomPotionAction(character=game_state.player.character),
                    AddRandomPotionAction(character=game_state.player.character),
                ]
            ))
        
        # Option 3: Buy 3 Potions - 40 Gold
        if game_state.player.gold >= 40:
            options.append(Option(
                name=LocalStr("events.woman_in_blue.option3"),
                actions=[
                    LoseGoldAction(amount=40),
                    AddRandomPotionAction(character=game_state.player.character),
                    AddRandomPotionAction(character=game_state.player.character),
                    AddRandomPotionAction(character=game_state.player.character),
                ]
            ))
        
        # Option 4: Leave - Lose 5% of Max HP
        options.append(Option(
            name=LocalStr("events.woman_in_blue.option4"),
            actions=[
                LoseHPAction(amount=game_state.player.max_hp // 20),  # 5% of max HP
            ]
        ))
        
        # Display options and wait for selection
        actions.append(InputRequestAction(
            title=LocalStr("events.woman_in_blue.title"),
            options=options
        ))
        
        return MultipleActionsResult(actions)
