"""Event: Vampires - Act 2 Event

Trade Strikes for Bites at Max HP cost.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction, RemoveAllStrikesAction
from actions.reward import LoseRelicAction
from actions.combat import LoseMaxHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless.bite import Bite
from relics.global_relics.common import BloodVial


@register_event(event_id='vampires', acts=[2], weight=100)
class Vampires(Event):
    """Vampires - Strikes to Bites for Max HP."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.vampires.description'
        ))
        
        # Check if player has Blood Vial
        has_blood_vial = any(
            isinstance(r, BloodVial) for r in game_state.player.relics
        )
        
        # Build options
        options = []
        
        if has_blood_vial:
            options.append(Option(
                name=LocalStr('events.vampires.offer_blood_vial'),
                actions=[
                    LoseRelicAction(relic_type=BloodVial),
                    RemoveAllStrikesAction(),
                    *[AddCardAction(card=Bite()) for _ in range(5)]
                ]
            ))
        
        options.extend([
            Option(
                name=LocalStr('events.vampires.accept'),
                actions=[
                    LoseMaxHPAction(amount=int(game_state.player.max_hp * 0.30)),
                    RemoveAllStrikesAction(),
                    *[AddCardAction(card=Bite()) for _ in range(5)]
                ]
            ),
            Option(
                name=LocalStr('events.vampires.refuse'),
                actions=[]
            )
        ])
        
        actions.append(InputRequestAction(
            title=LocalStr('events.vampires.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
