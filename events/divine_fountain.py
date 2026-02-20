"""Event: The Divine Fountain - Shrine Event (All Acts)

Remove all curses from the deck. Only appears if deck has at least one curse.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import RemoveCardAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='divine_fountain', floors='all', weight=100)
class DivineFountain(Event):
    """Divine Fountain - remove all curses."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if deck has at least one curse."""
        for card in game_state.player.deck:
            if hasattr(card, 'is_curse') and card.is_curse:
                return True
        return False
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.divine_fountain.description'
        ))
        
        # Get all curse cards and create remove actions
        curse_cards = [card for card in game_state.player.deck 
                       if hasattr(card, 'is_curse') and card.is_curse]
        remove_actions = [RemoveCardAction(card) for card in curse_cards]
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.divine_fountain.drink'),
                actions=remove_actions
            ),
            Option(
                name=LocalStr('events.divine_fountain.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.divine_fountain.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
