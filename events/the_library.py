"""Event: The Library - Act 2 Event

Choose from character cards or heal.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseAddRandomCardAction, ChooseObtainCardAction
from actions.combat import HealAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='the_library', floors='mid', weight=100)
class TheLibrary(Event):
    """The Library - choose card or heal."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Ascension 15+."""
        return game_state.ascension >= 15
    
    def trigger(self) -> BaseResult:
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
                    actions=[ChooseObtainCardAction(
                    total=20,
                    namespace=game_state.player.namespace,
                    encounter_type="shop",
                    use_rolling_offset=False,
                )]
            ),
            Option(
                name=LocalStr('events.the_library.sleep'),
                actions=[HealAction(percent=heal_percent)]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.the_library.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
