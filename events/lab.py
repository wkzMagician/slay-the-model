"""Event: Lab - Shrine Event (All Acts)

A laboratory that provides free potions.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddRandomPotionAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='lab', acts='shared', weight=100)
class Lab(Event):
    """Lab - obtain random potions."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.lab.description'
        ))
        
        # Ascension 15+ reduces potions from 3 to 2
        potion_count = 2 if game_state.ascension >= 15 else 3
        
        # Build options
        potion_actions = [AddRandomPotionAction(character=game_state.player.character) for _ in range(potion_count)]
        
        options = [
            Option(
                name=LocalStr('events.lab.search'),
                actions=potion_actions
            ),
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.lab.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
