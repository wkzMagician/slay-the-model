"""Event: Hypnotizing Colored Mushrooms - Act 1 Event (Floor 7+)

A mushroom event offering healing with a curse or a fight for a relic.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.base import LambdaAction
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction
from actions.reward import AddRelicAction
from actions.combat import HealAction, StartFightAction
from enemies.act1.fungi_beast import FungiBeast
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import OddMushroom
from cards.colorless import Parasite


@register_event(category='event', event_id='hypnotizing_mushrooms', acts=[1], weight=100)
class HypnotizingColoredMushrooms(Event):
    """Hypnotizing Colored Mushrooms - heal with curse or fight for relic."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Floor 7+ within Act 1."""
        # Use floor_in_act since this is an Act 1-only event
        return game_state.floor_in_act >= 7
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.hypnotizing_mushrooms.description'
        ))
        
        # Create fungi beast instances for combat
        fungi_beasts = [FungiBeast(), FungiBeast(), FungiBeast()]
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.hypnotizing_mushrooms.stomp'),
                detail=LocalStr('events.hypnotizing_mushrooms.stomp_effect'),
                actions=[
                    StartFightAction(
                        enemies=fungi_beasts,
                        escape_actions=[LambdaAction(self.end_event)],
                        victory_actions=[
                            AddRelicAction(relic=OddMushroom()),
                            LambdaAction(lambda: self.end_event()),
                        ]
                    )
                ]
            ),
            Option(
                name=LocalStr('events.hypnotizing_mushrooms.eat'),
                detail=LocalStr('events.hypnotizing_mushrooms.eat_effect'),
                actions=[
                    HealAction(percent=0.25),
                    AddCardAction(card=Parasite()),
                    LambdaAction(lambda: self.end_event()),
                ]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.hypnotizing_mushrooms.title'),
            options=options
        ))

        add_actions(actions)
