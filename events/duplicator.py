"""Event: Duplicator - Shrine Event (All Acts)

A shrine that allows the player to duplicate a card in their deck.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseCopyCardAction
from localization import LocalStr
from utils.option import Option


@register_event(event_id='duplicator', floors='all', weight=100)
class Duplicator(Event):
    """Duplicator shrine - allows duplicating a card."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.duplicator.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.duplicator.pray'),
                actions=[ChooseCopyCardAction()]
            ),
            Option(
                name=LocalStr('events.duplicator.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.duplicator.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
