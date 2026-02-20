"""Event: The Nest - Act 2 Event

Gold or Ritual Dagger card for HP.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddCardAction
from actions.reward import AddGoldAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless.ritual_dagger import RitualDagger


@register_event(event_id='the_nest', floors='mid', weight=100)
class TheNest(Event):
    """The Nest - gold or Ritual Dagger."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Ascension 15+."""
        return game_state.ascension >= 15
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.the_nest.description'
        ))
        
        # Gold: 99 normal, 50 on A15+
        gold_amount = 50 if game_state.ascension >= 15 else 99
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.the_nest.smash_and_grab'),
                actions=[AddGoldAction(amount=gold_amount)]
            ),
            Option(
                name=LocalStr('events.the_nest.stay_in_line'),
                actions=[
                    LoseHPAction(amount=6),
                    AddCardAction(card=RitualDagger())
                ]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.the_nest.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
