"""Event: Tomb of Lord Red Mask - Act 3 Event

Red Mask interaction (trade gold or wear for gold).
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddGoldAction, LoseGoldAction, AddRelicAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import RedMask


@register_event(event_id='tomb_of_lord_red_mask', floors='late', weight=100)
class TombOfLordRedMask(Event):
    """Tomb of Lord Red Mask - Red Mask interaction."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.tomb_of_lord_red_mask.description'
        ))
        
        # Check if player has Red Mask
        has_red_mask = any(
            isinstance(r, RedMask) for r in game_state.player.relics
        )
        
        # Build options based on mask status
        options = []
        
        if has_red_mask:
            options.extend([
                Option(
                    name=LocalStr('events.tomb_of_lord_red_mask.don_mask'),
                    actions=[AddGoldAction(amount=222)]
                ),
                Option(
                    name=LocalStr('events.tomb_of_lord_red_mask.leave'),
                    actions=[]
                )
            ])
        else:
            options.extend([
                Option(
                    name=LocalStr('events.tomb_of_lord_red_mask.offer_gold'),
                    actions=[
                        LoseGoldAction(amount='all'),
                        AddRelicAction(relic=RedMask())
                    ]
                ),
                Option(
                    name=LocalStr('events.tomb_of_lord_red_mask.leave'),
                    actions=[]
                )
            ])
        
        actions.append(SelectAction(
            title=LocalStr('events.tomb_of_lord_red_mask.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
