"""Event: Face Trader - Shrine Event (Act 1-2)

Trade HP for gold or gamble for face relics.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

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


@register_event(category='special', event_id='face_trader', acts=[1, 2], weight=100)
class FaceTrader(Event):
    """Face Trader - trade HP for gold or gamble for face relics."""
    
    def trigger(self) -> None:
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
                detail=LocalStr('events.face_trader.touch_detail', hp=int(game_state.player.max_hp * hp_percent), gold=gold_amount),
                actions=[
                    LoseHPAction(percent=hp_percent),
                    AddGoldAction(amount=gold_amount)
                ]
            ),
            Option(
                name=LocalStr('events.face_trader.trade'),
                detail=LocalStr('events.face_trader.trade_detail'),
                actions=[
                    # Receive one of the five face relics (20% each)
                    AddRelicAction(relic=get_rng("misc").choice([
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
                detail=LocalStr('events.no_effect'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.face_trader.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)
