"""Event: Masked Bandits - Act 2 Event

Pay all gold or fight for Red Mask relic.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.reward import LoseGoldAction, AddRelicAction, AddGoldAction
from actions.combat import StartFightAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import RedMask


@register_event(event_id='masked_bandits', floors='mid', weight=100)
class MaskedBandits(Event):
    """Masked Bandits - pay gold or fight for Red Mask."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.masked_bandits.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.masked_bandits.pay'),
                actions=[LoseGoldAction(amount='all')]
            ),
            Option(
                name=LocalStr('events.masked_bandits.fight'),
                actions=[
                    StartFightAction(enemies=['pointy', 'romeo', 'bear']),
                    AddRelicAction(relic=RedMask()),
                    AddGoldAction(amount=30),  # 25-35 gold
                    AddRandomCardAction()  # Card reward
                ]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.masked_bandits.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
