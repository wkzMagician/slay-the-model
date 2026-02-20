"""Event: Living Wall - Act 1 Event

A forced choice event where you must either remove, transform, or upgrade a card.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction, ChooseTransformCardAction, ChooseUpgradeCardAction
from localization import LocalStr
from utils.option import Option


@register_event(event_id='living_wall', floors='early', weight=100)
class LivingWall(Event):
    """Living Wall - forced choice of remove/transform/upgrade card."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.living_wall.description'
        ))
        
        # Build options (must choose one)
        options = [
            Option(
                name=LocalStr('events.living_wall.forget'),
                actions=[ChooseRemoveCardAction()]
            ),
            Option(
                name=LocalStr('events.living_wall.change'),
                actions=[ChooseTransformCardAction()]
            ),
            Option(
                name=LocalStr('events.living_wall.grow'),
                actions=[ChooseUpgradeCardAction()]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.living_wall.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
