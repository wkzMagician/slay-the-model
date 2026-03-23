"""Event: Falling - Act 3 Event

Forced card loss by type (Skill, Power, or Attack).
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import RemoveRandomCardAction
from localization import LocalStr
from utils.option import Option
from utils.types import CardType


@register_event(event_id='falling', acts=[3], weight=100)
class Falling(Event):
    """Falling - forced card loss by type."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.falling.description'
        ))
        
        # Build options - must choose one
        options = [
            Option(
                name=LocalStr('events.falling.land'),
                actions=[RemoveRandomCardAction(card_type=CardType.SKILL)]
            ),
            Option(
                name=LocalStr('events.falling.channel'),
                actions=[RemoveRandomCardAction(card_type=CardType.POWER)]
            ),
            Option(
                name=LocalStr('events.falling.strike'),
                actions=[RemoveRandomCardAction(card_type=CardType.ATTACK)]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.falling.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
