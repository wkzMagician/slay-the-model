"""Event: Mysterious Sphere - Act 3 Event

Fight 2 Orb Walkers for relic reward.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from actions.combat import StartFightAction
from utils.registry import get_registered
from localization import LocalStr
from utils.option import Option


@register_event(category='event', event_id='mysterious_sphere', acts=[3], weight=100)
class MysteriousSphere(Event):
    """Mysterious Sphere - fight for relic."""
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.mysterious_sphere.description'
        ))
        
        # Create Orb Walker instances for combat
        orb_walker_class = get_registered("enemy", 'orb_walker')
        orb_walkers = [orb_walker_class(), orb_walker_class()] if orb_walker_class else []
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.mysterious_sphere.open_sphere'),
                detail=LocalStr('events.mysterious_sphere.open_sphere_detail'),
                actions=[
                    StartFightAction(
                        enemies=orb_walkers,
                        victory_actions=[
                            AddRandomRelicAction(rarity='rare'),
                            AddGoldAction(amount=get_rng("misc").randint(45, 55)),
                            AddRandomCardAction()
                        ]
                    )
                ]
            ),
            Option(
                name=LocalStr('events.mysterious_sphere.leave'),
                detail=LocalStr('events.no_effect'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.mysterious_sphere.title'),
            options=options
        ))
        
        self.end_event()
        from engine.game_state import game_state
        add_actions(actions)
