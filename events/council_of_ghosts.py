"""Event: Council of Ghosts - Act 2 Event

Trade 50% Max HP for 5 Apparition cards (3 on A15+).
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction
from actions.combat import LoseMaxHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Apparition


@register_event(event_id='council_of_ghosts', acts=[2], weight=100)
class CouncilOfGhosts(Event):
    """Council of Ghosts - Max HP for Apparition cards."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.council_of_ghosts.description'
        ))
        
        # Number of apparitions: 5 normal, 3 on A15+
        apparition_count = 3 if game_state.ascension >= 15 else 5
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.council_of_ghosts.accept'),
                actions=[
                    # Lose 50% of Max HP
                    LoseMaxHPAction(amount=game_state.player.max_hp // 2),
                    *[AddCardAction(card=Apparition()) for _ in range(apparition_count)]
                ]
            ),
            Option(
                name=LocalStr('events.council_of_ghosts.refuse'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.council_of_ghosts.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
