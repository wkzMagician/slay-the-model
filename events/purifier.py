"""Event: Purifier - Shrine Event (All Acts)

A shrine that allows removing a card from the deck.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction
from localization import LocalStr
from utils.option import Option


@register_event(event_id='purifier', acts='shared', weight=100)
class Purifier(Event):
    """Purifier shrine - remove a card."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.purifier.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.purifier.pray'),
                actions=[ChooseRemoveCardAction()]
            ),
            Option(
                name=LocalStr('events.purifier.leave'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.purifier.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
