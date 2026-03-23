"""Event: World of Goop - Act 1 Event

Forced gold loss or gain gold at HP cost.
"""

import random
from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddGoldAction, LoseGoldAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='world_of_goop', acts=[1], weight=100)
class WorldOfGoop(Event):
    """World of Goop - lose gold or gain gold for HP."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Ascension 15+."""
        return game_state.ascension >= 15
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.world_of_goop.description'
        ))
        
        # Gold loss: 20-50 normal, 35-75 on A15+
        if game_state.ascension >= 15:
            gold_loss = min(random.randint(35, 75), game_state.player.gold)
        else:
            gold_loss = min(random.randint(20, 50), game_state.player.gold)
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.world_of_goop.gather'),
                actions=[
                    LoseHPAction(amount=11),
                    AddGoldAction(amount=75)
                ]
            ),
            Option(
                name=LocalStr('events.world_of_goop.leave'),
                actions=[LoseGoldAction(amount=gold_loss)]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.world_of_goop.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
