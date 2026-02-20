"""Event: Mysterious Sphere - Act 3 Event

Fight 2 Orb Walkers for relic reward.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from actions.combat import StartFightAction
from localization import LocalStr
from utils.option import Option


@register_event(event_id='mysterious_sphere', floors='late', weight=100)
class MysteriousSphere(Event):
    """Mysterious Sphere - fight for relic."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.mysterious_sphere.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.mysterious_sphere.open_sphere'),
                actions=[
                    StartFightAction(enemies=['orb_walker', 'orb_walker']),
                    AddRandomRelicAction(rarity='rare'),
                    AddGoldAction(amount=50),  # 45-55 gold
                    AddRandomCardAction()
                ]
            ),
            Option(
                name=LocalStr('events.mysterious_sphere.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.mysterious_sphere.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
