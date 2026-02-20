"""Event: Sensory Stone - Act 3 Event

Colorless cards for HP trade.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option


@register_event(event_id='sensory_stone', floors='late', weight=100)
class SensoryStone(Event):
    """Sensory Stone - colorless cards for HP."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.sensory_stone.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.sensory_stone.recall_1'),
                actions=[
                    AddRandomCardAction(namespace='colorless', rarity='uncommon_or_rare')
                ]
            ),
            Option(
                name=LocalStr('events.sensory_stone.recall_2'),
                actions=[
                    LoseHPAction(amount=5),
                    AddRandomCardAction(namespace='colorless', rarity='uncommon_or_rare'),
                    AddRandomCardAction(namespace='colorless', rarity='uncommon_or_rare')
                ]
            ),
            Option(
                name=LocalStr('events.sensory_stone.recall_3'),
                actions=[
                    LoseHPAction(amount=10),
                    AddRandomCardAction(namespace='colorless', rarity='uncommon_or_rare'),
                    AddRandomCardAction(namespace='colorless', rarity='uncommon_or_rare'),
                    AddRandomCardAction(namespace='colorless', rarity='uncommon_or_rare')
                ]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.sensory_stone.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
