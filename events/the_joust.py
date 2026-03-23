"""Event: The Joust - Act 2 Shrine Event

Bet 50 gold for 100 or 250 gold reward.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddGoldAction, LoseGoldAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='the_joust', acts=[2], weight=100)
class TheJoust(Event):
    """The Joust - bet gold for reward."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if player has 50+ gold."""
        return game_state.player.gold >= 50
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.the_joust.description'
        ))
        
        # Build options
        # Murderer: 70% chance to win 100 gold (EV: +20 gold)
        # Owner: 30% chance to win 250 gold (EV: +25 gold)
        options = [
            Option(
                name=LocalStr('events.the_joust.murderer'),
                actions=[
                    LoseGoldAction(amount=50),
                    AddGoldAction(amount=100, chance=0.70)
                ],
                enabled=game_state.player.gold >= 50
            ),
            Option(
                name=LocalStr('events.the_joust.owner'),
                actions=[
                    LoseGoldAction(amount=50),
                    AddGoldAction(amount=250, chance=0.30)
                ],
                enabled=game_state.player.gold >= 50
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.the_joust.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
