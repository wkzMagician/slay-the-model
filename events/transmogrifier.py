"""Event: Transmogrifier - Shrine Event (All Acts)

A shrine that allows transforming a card into a random card.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseTransformCardAction
from localization import LocalStr
from utils.option import Option


@register_event(event_id='transmogrifier', floors='all', weight=100)
class Transmogrifier(Event):
    """Transmogrifier shrine - transform a card."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.transmogrifier.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.transmogrifier.pray'),
                actions=[ChooseTransformCardAction()]
            ),
            Option(
                name=LocalStr('events.transmogrifier.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.transmogrifier.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
