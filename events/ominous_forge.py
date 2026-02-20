"""Event: Ominous Forge - Event (All Acts)

A forge that allows upgrading a card or obtaining Warped Tongs with a curse.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseUpgradeCardAction, AddCardAction
from actions.reward import AddRelicAction
from localization import LocalStr
from utils.option import Option
from relics.global_relics.event import WarpedTongs
from cards.colorless import Pain


@register_event(event_id='ominous_forge', floors='all', weight=100)
class OminousForge(Event):
    """Ominous Forge - upgrade card or get Warped Tongs + Pain."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.ominous_forge.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.ominous_forge.forge'),
                actions=[ChooseUpgradeCardAction()]
            ),
            Option(
                name=LocalStr('events.ominous_forge.rummage'),
                actions=[
                    AddRelicAction(relic=WarpedTongs()),
                    AddCardAction(card=Pain())
                ]
            ),
            Option(
                name=LocalStr('events.ominous_forge.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.ominous_forge.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
