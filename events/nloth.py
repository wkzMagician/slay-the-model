"""Event: N'loth - Act 2 Shrine Event

Trade a relic for N'loth's Gift (duplicate obtained cards 50% chance).
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddRelicAction, LoseRelicAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import NlothGift


@register_event(event_id='nloth', floors='mid', weight=100)
class Nloth(Event):
    """N'loth - trade relic for N'loth's Gift."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if player has 2+ relics."""
        return len(game_state.player.relics) >= 2
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.nloth.description'
        ))
        
        # Build options - offer to trade a relic
        options = [
            Option(
                name=LocalStr('events.nloth.offer_relic'),
                actions=[
                    # TODO: Implement ChooseLoseRelicAction - for now use LoseRelicAction
                    LoseRelicAction(relic=game_state.player.relics[0] if game_state.player.relics else None),
                    AddRelicAction(relic=NlothGift())
                ]
            ),
            Option(
                name=LocalStr('events.nloth.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.nloth.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
