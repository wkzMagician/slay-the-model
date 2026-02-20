"""Event: A Note For Yourself - Shrine Event (All Acts, disabled A15+)

Cross-run card storage event that allows receiving a card from previous run
and storing a card for future runs.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddCardAction, ChooseRemoveCardAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='a_note_for_yourself', floors='all', weight=100)
class ANoteForYourself(Event):
    """A Note For Yourself - cross-run card storage."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Disabled on Ascension 15+ and Daily Climb."""
        if game_state.ascension >= 15:
            return False
        # Also disabled in Daily Climb (not implemented yet)
        return True
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.a_note_for_yourself.description'
        ))
        
        # TODO: Implement cross-run card storage system
        # For now, implement basic version without persistence
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.a_note_for_yourself.take_and_give'),
                actions=[
                    # AddCardAction(card=stored_card),  # Would add stored card
                    # ChooseLoseCardAction()  # Would store a card
                ]
            ),
            Option(
                name=LocalStr('events.a_note_for_yourself.ignore'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.a_note_for_yourself.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
