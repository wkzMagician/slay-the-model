"""Event: Secret Portal - Act 3 Shrine Event

Skip to boss if 800+ seconds elapsed.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.misc import SkipToBossAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='secret_portal', acts=[3], weight=100)
class SecretPortal(Event):
    """Secret Portal - skip to boss."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if 800+ seconds (13:20) elapsed."""
        return game_state.elapsed_time >= 800 # todo: 在游戏中增加计时策略
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.secret_portal.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.secret_portal.enter'),
                actions=[SkipToBossAction()]
            ),
            Option(
                name=LocalStr('events.secret_portal.leave'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.secret_portal.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
