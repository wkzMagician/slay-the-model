"""Event: The Moai Head - Act 3 Event

Heal or trade Golden Idol for gold.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddGoldAction, LoseRelicAction
from actions.combat import HealAction, LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import GoldenIdol


@register_event(event_id='the_moai_head', acts=[3], weight=100)
class TheMoaiHead(Event):
    """The Moai Head - heal or trade Golden Idol."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if HP <= 50% or have Golden Idol."""
        hp_low = game_state.player.hp <= game_state.player.max_hp * 0.50
        has_golden_idol = any(
            isinstance(r, GoldenIdol) for r in game_state.player.relics
        )
        return hp_low or has_golden_idol
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.the_moai_head.description'
        ))
        
        # Check if player has Golden Idol
        has_golden_idol = any(
            isinstance(r, GoldenIdol) for r in game_state.player.relics
        )
        
        # HP cost for heal: 12.5% normal, 18% on A15+
        hp_percent = 0.18 if game_state.ascension >= 15 else 0.125
        
        # Build options
        options = []
        
        if has_golden_idol:
            options.append(Option(
                name=LocalStr('events.the_moai_head.offer_golden_idol'),
                actions=[
                    LoseRelicAction(relic_type=GoldenIdol),
                    AddGoldAction(amount=333)
                ]
            ))
        
        options.extend([
            Option(
                name=LocalStr('events.the_moai_head.jump_inside'),
                actions=[
                    HealAction(percent=1.0),
                    LoseHPAction(percent=hp_percent)
                ]
            ),
            Option(
                name=LocalStr('events.the_moai_head.leave'),
                actions=[]
            )
        ])
        
        actions.append(InputRequestAction(
            title=LocalStr('events.the_moai_head.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
