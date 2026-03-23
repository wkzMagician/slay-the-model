"""Event: Golden Idol - Act 1 Event

A relic event with trap consequences. Taking the idol triggers a trap.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction
from actions.reward import AddRelicAction
from actions.combat import LoseHPAction, ModifyMaxHpAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import GoldenIdol
from cards.colorless import Injury


@register_event(event_id='golden_idol', acts=[1], weight=100)
class GoldenIdolEvent(Event):
    """Golden Idol - take relic and face trap consequences."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.golden_idol.description'
        ))
        
        # Calculate HP amounts (ModifyMaxHpAction uses amount, not percent)
        smash_percent = 0.35 if game_state.ascension >= 15 else 0.25
        hide_percent = 0.10 if game_state.ascension >= 15 else 0.08
        # Calculate negative amount for losing MaxHP
        hide_hp_loss = -int(game_state.player.max_hp * hide_percent)
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.golden_idol.take'),
                actions=[
                    AddRelicAction(relic=GoldenIdol()),
                    # Triggers trap - player must choose:
                    InputRequestAction(
                        title=LocalStr('events.golden_idol.trap'),
                        options=[
                            Option(
                                name=LocalStr('events.golden_idol.outrun'),
                                actions=[AddCardAction(card=Injury())]
                            ),
                            Option(
                                name=LocalStr('events.golden_idol.smash'),
                                actions=[LoseHPAction(percent=smash_percent)]
                            ),
                            Option(
                                name=LocalStr('events.golden_idol.hide'),
                                actions=[ModifyMaxHpAction(amount=hide_hp_loss)]
                            )
                        ]
                    )
                ]
            ),
            Option(
                name=LocalStr('events.golden_idol.leave'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.golden_idol.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
