"""Event: Face Trader - Shrine Event (Act 1-2)

Trade HP for gold or gamble for face relics.
"""

import random
from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddGoldAction, AddRelicAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import (
    CultistHeadpiece, FaceOfCleric, GremlinVisage, 
    NlothHungryFace, SsserpentHead
)


@register_event(event_id='face_trader', acts=[1, 2], weight=100)
class FaceTrader(Event):
    """Face Trader - trade HP for gold or gamble for face relics."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.face_trader.description'
        ))
        
        # Calculate HP loss percentage
        hp_percent = 0.15 if game_state.ascension >= 15 else 0.10
        gold_amount = 50 if game_state.ascension >= 15 else 75
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.face_trader.touch'),
                actions=[
                    LoseHPAction(percent=hp_percent),
                    AddGoldAction(amount=gold_amount)
                ]
            ),
            Option(
                name=LocalStr('events.face_trader.trade'),
                actions=[
                    # Receive one of the five face relics (20% each)
                    AddRelicAction(relic=random.choice([
                        CultistHeadpiece(),
                        FaceOfCleric(),
                        GremlinVisage(),
                        NlothHungryFace(),
                        SsserpentHead()
                    ]))
                ]
            ),
            Option(
                name=LocalStr('events.face_trader.leave'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.face_trader.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
