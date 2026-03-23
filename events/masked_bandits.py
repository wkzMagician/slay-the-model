"""Event: Masked Bandits - Act 2 Event

Pay all gold or fight for Red Mask relic.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.reward import LoseGoldAction, AddRelicAction, AddGoldAction
from actions.combat import StartFightAction
from utils.registry import get_registered
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import RedMask


@register_event(event_id='masked_bandits', acts=[2], weight=100)
class MaskedBandits(Event):
    """Masked Bandits - pay gold or fight for Red Mask."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.masked_bandits.description'
        ))
        
        # Create enemy instances for combat
        pointy_class = get_registered("enemy", 'pointy')
        romeo_class = get_registered("enemy", 'romeo')
        bear_class = get_registered("enemy", 'bear')
        bandits = []
        if pointy_class:
            bandits.append(pointy_class())
        if romeo_class:
            bandits.append(romeo_class())
        if bear_class:
            bandits.append(bear_class())
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.masked_bandits.pay'),
                actions=[LoseGoldAction(amount='all')]
            ),
            Option(
                name=LocalStr('events.masked_bandits.fight'),
                actions=[
                    StartFightAction(
                        enemies=bandits,
                        victory_actions=[AddRelicAction(relic=RedMask())]
                    )
                ]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.masked_bandits.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
