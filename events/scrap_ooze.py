"""Event: Scrap Ooze - Act 1 Event (A15+)

An event where you reach into an ooze for a chance to get a relic at HP cost.
"""

import random
from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddRandomRelicAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='scrap_ooze', acts=[1], weight=100)
class ScrapOoze(Event):
    """Scrap Ooze - HP for relic chance."""
    
    def __init__(self):
        super().__init__()
        self.attempt_count = 0
        self.relic_obtained = False
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.scrap_ooze.description'
        ))
        
        # Base chance starts at 25%, +10% per attempt
        relic_chance = 0.25 + (self.attempt_count * 0.10)
        # HP cost: 3 base + 1 per attempt (5 base on A15+)
        base_hp = 5 if game_state.ascension >= 15 else 3
        hp_cost = base_hp + self.attempt_count
        
        # Build options
        options = []
        
        if not self.relic_obtained:
            # Check if relic is obtained this attempt
            if random.random() < relic_chance:
                options.append(Option(
                    name=LocalStr('events.scrap_ooze.reach'),
                    actions=[AddRandomRelicAction()]
                ))
                self.relic_obtained = True
            else:
                options.append(Option(
                    name=LocalStr('events.scrap_ooze.reach'),
                    actions=[LoseHPAction(amount=hp_cost)]
                ))
                self.attempt_count += 1
        
        # Leave option
        options.append(Option(
            name=LocalStr('events.scrap_ooze.leave'),
            actions=[]
        ))
        
        actions.append(InputRequestAction(
            title=LocalStr('events.scrap_ooze.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
