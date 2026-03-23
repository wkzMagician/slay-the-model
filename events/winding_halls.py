"""Event: Winding Halls - Act 3 Event

Trade-offs for cards/heal (Madness, heal + Writhe, or lose HP).
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction
from actions.combat import HealAction, LoseHPAction, ModifyMaxHpAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless.madness import Madness
from cards.colorless.writhe import Writhe


@register_event(event_id='winding_halls', acts=[3], weight=100)
class WindingHalls(Event):
    """Winding Halls - trade-offs for cards/heal."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Ascension 15+."""
        return game_state.ascension >= 15
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.winding_halls.description'
        ))
        
        # HP percentages: 12.5% normal, 18% on A15+
        hp_percent = 0.18 if game_state.ascension >= 15 else 0.125
        heal_percent = 0.20 if game_state.ascension >= 15 else 0.25
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.winding_halls.embrace_madness'),
                actions=[
                    LoseHPAction(percent=hp_percent),
                    AddCardAction(card=Madness()),
                    AddCardAction(card=Madness())
                ]
            ),
            Option(
                name=LocalStr('events.winding_halls.focus'),
                actions=[
                    HealAction(percent=heal_percent),
                    AddCardAction(card=Writhe())
                ]
            ),
            Option(
                name=LocalStr('events.winding_halls.retrace'),
                actions=[ModifyMaxHpAction(amount=-0.05*game_state.player.max_hp)]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.winding_halls.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
