"""Event: Hypnotizing Colored Mushrooms - Act 1 Event (Floor 7+)

A mushroom event offering healing with a curse or a fight for a relic.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddCardAction
from actions.reward import AddRelicAction
from actions.combat import HealAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import OddMushroom
from cards.colorless import Parasite


@register_event(event_id='hypnotizing_mushrooms', floors='early', weight=100)
class HypnotizingColoredMushrooms(Event):
    """Hypnotizing Colored Mushrooms - heal with curse or fight for relic."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Floor 7+."""
        return game_state.current_floor >= 7
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.hypnotizing_mushrooms.description'
        ))
        
        # Build options
        # TODO: Add StartFightAction when available
        # Current implementation provides the relic directly without fight
        options = [
            Option(
                name=LocalStr('events.hypnotizing_mushrooms.stomp'),
                actions=[
                    AddRelicAction(relic=OddMushroom())
                ]
            ),
            Option(
                name=LocalStr('events.hypnotizing_mushrooms.eat'),
                actions=[
                    HealAction(percent=0.25),
                    AddCardAction(card=Parasite())
                ]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.hypnotizing_mushrooms.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
