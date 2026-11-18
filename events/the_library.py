"""Event: The Library - Act 2 Event

Choose from character cards or heal.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import ChooseAddRandomCardAction, ChooseObtainCardAction
from actions.combat import HealAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(category='event', event_id='the_library', acts=[2], weight=100)
class TheLibrary(Event):
    """The Library - choose card or heal."""
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.the_library.description'
        ))
        
        # Heal percentage: 33% normal, 20% on A15+
        heal_percent = 0.20 if game_state.ascension >= 15 else 0.33
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.the_library.read'),
                detail=LocalStr('events.the_library.read_detail'),
                    actions=[ChooseObtainCardAction(
                    total=20,
                    namespace=game_state.player.namespace,
                    selection_kind="library",
                    use_rolling_offset=False,
                    can_skip=False
                )]
            ),
            Option(
                name=LocalStr('events.the_library.sleep'),
                detail=LocalStr('events.the_library.sleep_detail', heal=int(game_state.player.max_hp * heal_percent)),
                actions=[HealAction(percent=heal_percent)]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.the_library.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)
