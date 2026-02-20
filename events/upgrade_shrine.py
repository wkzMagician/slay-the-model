"""Event: Upgrade Shrine - Shrine Event (All Acts)

A shrine that allows upgrading a card.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseUpgradeCardAction
from localization import LocalStr
from utils.option import Option


@register_event(event_id='upgrade_shrine', floors='all', weight=100)
class UpgradeShrine(Event):
    """Upgrade shrine - upgrade a card."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.upgrade_shrine.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.upgrade_shrine.pray'),
                actions=[ChooseUpgradeCardAction()]
            ),
            Option(
                name=LocalStr('events.upgrade_shrine.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.upgrade_shrine.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
