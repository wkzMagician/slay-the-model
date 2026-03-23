"""Event: Shining Light - Act 1 Event (A15+)

Upgrade 2 random cards at the cost of Max HP.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import UpgradeRandomCardAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='shining_light', acts=[1], weight=100)
class ShiningLight(Event):
    """Shining Light - upgrade cards for HP."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.shining_light.description'
        ))
        
        # HP cost: 20% on normal, 30% on A15+
        hp_percent = 0.30 if game_state.ascension >= 15 else 0.20
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.shining_light.enter'),
                actions=[
                    LoseHPAction(percent=hp_percent),
                    UpgradeRandomCardAction(),
                    UpgradeRandomCardAction()  # Two upgrades
                ]
            ),
            Option(
                name=LocalStr('events.shining_light.leave'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.shining_light.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
