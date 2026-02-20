"""Event: Dead Adventurer - Act 1 Event (Floor 7+)

A risk/reward event where you search for loot with increasing chance of elite ambush.
Note: Elite fight mechanic simplified - TODO: implement StartEliteFightAction
"""

import random
from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from localization import LocalStr
from utils.option import Option
from utils.types import RarityType
from engine.game_state import game_state


@register_event(event_id='dead_adventurer', floors='early', weight=100)
class DeadAdventurer(Event):
    """Dead Adventurer - search for loot with elite risk."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Floor 7+."""
        return game_state.current_floor >= 7
    
    def __init__(self):
        super().__init__()
        self.search_count = 0
        self.found_gold = False
        self.found_relic = False
        self.found_nothing = False
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.dead_adventurer.description'
        ))
        
        # Build options
        options = []
        
        # Option to continue searching (max 3 times)
        # Note: Elite fight mechanic simplified - just provides loot
        if self.search_count < 3:
            # Determine what can be found (in order)
            if not self.found_gold:
                options.append(Option(
                    name=LocalStr('events.dead_adventurer.search'),
                    actions=[AddGoldAction(amount=30)]
                ))
            elif not self.found_relic:
                options.append(Option(
                    name=LocalStr('events.dead_adventurer.search'),
                    actions=[AddRandomRelicAction(rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE])]
                ))
            elif not self.found_nothing:
                options.append(Option(
                    name=LocalStr('events.dead_adventurer.search'),
                    actions=[DisplayTextAction(text_key='events.dead_adventurer.nothing')]
                ))
        
        # Leave option
        options.append(Option(
            name=LocalStr('events.dead_adventurer.leave'),
            actions=[]
        ))
        
        actions.append(SelectAction(
            title=LocalStr('events.dead_adventurer.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
