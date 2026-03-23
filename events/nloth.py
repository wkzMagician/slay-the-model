"""Event: N'loth - Act 2 Shrine Event

Trade a relic for N'loth's Gift (50% chance to duplicate obtained cards).
"""

import random

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddRelicAction, LoseRelicAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import NlothGift


@register_event(event_id='nloth', acts=[2], weight=100)
class Nloth(Event):
    """N'loth - trade a relic for N'loth's Gift (50% chance to duplicate obtained cards)."""
    
    def __init__(self):
        super().__init__()
        self.offered_relics = []
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if player has 2+ relics."""
        return len(game_state.player.relics) >= 2
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Select 2 random relics to offer on first trigger
        if not self.offered_relics and len(game_state.player.relics) >= 2:
            self.offered_relics = random.sample(
                list(game_state.player.relics), 
                min(2, len(game_state.player.relics))
            )
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.nloth.description'
        ))
        
        # Build options - each offered relic as separate choice
        options = []
        
        for relic in self.offered_relics:
            # Get relic display name
            relic_name = relic.name if hasattr(relic, 'name') else str(relic.__class__.__name__)
            
            options.append(Option(
                name=LocalStr(f'Trade {relic_name}'),
                actions=[
                    LoseRelicAction(relic=relic),
                    AddRelicAction(relic=NlothGift())
                ]
            ))
        
        # Leave option
        options.append(Option(
            name=LocalStr('events.nloth.leave'),
            actions=[]
        ))
        
        actions.append(InputRequestAction(
            title=LocalStr('events.nloth.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
