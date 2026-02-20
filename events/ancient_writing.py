"""Event: Ancient Writing - Act 2 Event

A choice event where you can remove a card or upgrade all Strikes and Defends.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction, UpgradeRandomCardAction
# TODO: Create UpgradeAllStrikesAndDefendsAction in actions.card
from localization import LocalStr
from utils.option import Option


@register_event(event_id='ancient_writing', floors='mid', weight=100)
class AncientWriting(Event):
    """Ancient Writing - remove card or upgrade Strikes/Defends."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.ancient_writing.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.ancient_writing.elegance'),
                actions=[ChooseRemoveCardAction()]
            ),
            Option(
                name=LocalStr('events.ancient_writing.simplicity'),
                # TODO: Create UpgradeAllStrikesAndDefendsAction
                # For now, upgrade 2 random cards as placeholder
                actions=[UpgradeRandomCardAction(), UpgradeRandomCardAction()]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.ancient_writing.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
