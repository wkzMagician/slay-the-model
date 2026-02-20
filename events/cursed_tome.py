"""Event: Cursed Tome - Act 2 Event

HP for random boss relic (book type).
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddRandomRelicAction
from utils.types import RarityType
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='cursed_tome', floors='mid', weight=100)
class CursedTome(Event):
    """Cursed Tome - HP for boss relic."""
    
    def __init__(self):
        super().__init__()
        self.read_count = 0
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.cursed_tome.description'
        ))
        
        # HP costs: 1+2+3 for reading, then 10 (15 on A15+) for relic
        hp_cost = 15 if game_state.ascension >= 15 else 10
        
        # Build options based on state
        options = []
        
        if self.read_count < 3:
            # Reading phase
            read_hp = self.read_count + 1  # 1, 2, 3
            options.append(Option(
                name=LocalStr('events.cursed_tome.read'),
                actions=[LoseHPAction(amount=read_hp)]
            ))
            self.read_count += 1
        else:
            # After 3 reads, can take tome or stop
            options.append(Option(
                name=LocalStr('events.cursed_tome.take'),
                actions=[
                    LoseHPAction(amount=hp_cost),
                    AddRandomRelicAction(rarities=[RarityType.BOSS])
                ]
            ))
            options.append(Option(
                name=LocalStr('events.cursed_tome.stop'),
                actions=[LoseHPAction(amount=3)]
            ))
        
        options.append(Option(
            name=LocalStr('events.cursed_tome.leave'),
            actions=[]
        ))
        
        actions.append(SelectAction(
            title=LocalStr('events.cursed_tome.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
