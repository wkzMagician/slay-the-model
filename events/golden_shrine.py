"""Event: Golden Shrine - Shrine Event (All Acts)

A shrine that offers gold or gold with a curse.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddGoldAction
from actions.card import AddCardAction
from localization import LocalStr
from utils.option import Option
from cards.colorless import Regret


@register_event(event_id='golden_shrine', acts='shared', weight=100)
class GoldenShrine(Event):
    """Golden shrine - gain gold or gold with curse."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.golden_shrine.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.golden_shrine.pray'),
                actions=[AddGoldAction(amount=100)]
            ),
            Option(
                name=LocalStr('events.golden_shrine.desecrate'),
                actions=[
                    AddGoldAction(amount=275),
                    AddCardAction(card=Regret())
                ]
            ),
            Option(
                name=LocalStr('events.golden_shrine.leave'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.golden_shrine.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
