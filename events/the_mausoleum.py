"""Event: The Mausoleum - Act 2 Event

Relic with 50% (100% A15+) Writhe curse chance.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction
from actions.reward import AddRandomRelicAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Writhe


@register_event(event_id='the_mausoleum', acts=[2], weight=100)
class TheMausoleum(Event):
    """The Mausoleum - relic with curse risk."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.the_mausoleum.description'
        ))
        
        # Curse chance: 50% normal, 100% on A15+
        curse_chance = 1.0 if game_state.ascension >= 15 else 0.50
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.the_mausoleum.open_coffin'),
                actions=[
                    AddRandomRelicAction(),
                    AddCardAction(card=Writhe(), chance=curse_chance)
                ]
            ),
            Option(
                name=LocalStr('events.the_mausoleum.leave'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.the_mausoleum.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
