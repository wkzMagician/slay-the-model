"""Event: Match and Keep - Shrine Event (All Acts)

A card matching minigame where you flip cards and match pairs to add them to your deck.
"""

import random
from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddCardAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='match_and_keep', floors='all', weight=100)
class MatchAndKeep(Event):
    """Match and Keep - card matching minigame."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.match_and_keep.description'
        ))
        
        # TODO: Implement full matching minigame
        # - 12 face-down cards
        # - 5 tries to match pairs
        # - Always includes 1 Colorless card pair and 1 Curse pair
        # - Cards stay revealed when matched
        
        # For now, simplified version that adds random cards
        # In full implementation, this would be an interactive minigame
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.match_and_keep.play'),
                actions=[
                    # Would trigger matching minigame
                    # Add matched cards to deck
                ]
            ),
            Option(
                name=LocalStr('events.match_and_keep.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.match_and_keep.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
