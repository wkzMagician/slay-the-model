"""Event: Pleading Vagrant - Act 2 Event

Gold for relic or free relic with Shame curse.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddCardAction
from actions.reward import AddRandomRelicAction, LoseGoldAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Shame


@register_event(event_id='pleading_vagrant', floors='mid', weight=100)
class PleadingVagrant(Event):
    """Pleading Vagrant - gold for relic or free relic + curse."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if player has 75+ gold for gold option."""
        return game_state.player.gold >= 75
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.pleading_vagrant.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.pleading_vagrant.offer_gold'),
                actions=[
                    LoseGoldAction(amount=85),
                    AddRandomRelicAction()
                ],
                enabled=game_state.player.gold >= 85
            ),
            Option(
                name=LocalStr('events.pleading_vagrant.rob'),
                actions=[
                    AddRandomRelicAction(),
                    AddCardAction(card=Shame())
                ]
            ),
            Option(
                name=LocalStr('events.pleading_vagrant.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.pleading_vagrant.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
