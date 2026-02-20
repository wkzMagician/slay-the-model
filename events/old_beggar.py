"""Event: Old Beggar - Act 2 Event

Pay gold to remove a card.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction
from actions.reward import LoseGoldAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='old_beggar', floors='mid', weight=100)
class OldBeggar(Event):
    """Old Beggar - pay gold to remove card."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if player has 75+ gold."""
        return game_state.player.gold >= 75
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.old_beggar.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.old_beggar.offer_gold'),
                actions=[
                    LoseGoldAction(amount=75),
                    ChooseRemoveCardAction()
                ],
                enabled=game_state.player.gold >= 75
            ),
            Option(
                name=LocalStr('events.old_beggar.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.old_beggar.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
