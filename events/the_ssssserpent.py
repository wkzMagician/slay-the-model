"""Event: The Ssssserpent - Act 1 Event

Trade for gold at the cost of receiving a curse.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddCardAction
from actions.reward import AddGoldAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Doubt


@register_event(event_id='the_ssssserpent', floors='early', weight=100)
class TheSsssserpent(Event):
    """The Ssssserpent - gold for curse."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.the_ssssserpent.description'
        ))
        
        # Gold amount: 175 normal, 150 on A15+
        gold_amount = 150 if game_state.ascension >= 15 else 175
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.the_ssssserpent.agree'),
                actions=[
                    AddGoldAction(amount=gold_amount),
                    AddCardAction(card=Doubt(), dest_pile="master_deck")
                ]
            ),
            Option(
                name=LocalStr('events.the_ssssserpent.disagree'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.the_ssssserpent.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
