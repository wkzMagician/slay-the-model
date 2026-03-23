"""Event: Hypnotizing Colored Mushrooms - Act 1 Event (Floor 7+)

A mushroom event offering healing with a curse or a fight for a relic.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction
from actions.reward import AddRelicAction
from actions.combat import HealAction, StartFightAction
from utils.registry import get_registered
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import OddMushroom
from cards.colorless import Parasite


@register_event(event_id='hypnotizing_mushrooms', acts=[1], weight=100)
class HypnotizingColoredMushrooms(Event):
    """Hypnotizing Colored Mushrooms - heal with curse or fight for relic."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Floor 7+ within Act 1."""
        # Use floor_in_act since this is an Act 1-only event
        return game_state.floor_in_act >= 7
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.hypnotizing_mushrooms.description'
        ))
        
        # Create fungi beast instances for combat
        fungi_beast_class = get_registered("enemy", 'fungi_beast')
        fungi_beasts = [fungi_beast_class(), fungi_beast_class(), fungi_beast_class()] if fungi_beast_class else []
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.hypnotizing_mushrooms.stomp'),
                actions=[
                    StartFightAction(
                        enemies=fungi_beasts,
                        victory_actions=[
                            AddRelicAction(relic=OddMushroom())
                        ]
                    )
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
        
        actions.append(InputRequestAction(
            title=LocalStr('events.hypnotizing_mushrooms.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
