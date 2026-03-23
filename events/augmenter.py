"""Event: Augmenter - Act 2 Event

Exclusive source of J.A.X. card and Mutagenic Strength relic.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction, ChooseTransformCardAction
from actions.reward import AddRelicAction
from localization import LocalStr
from utils.option import Option
from cards.colorless import JAX
from relics.global_relics.event import MutagenicStrength


@register_event(event_id='augmenter', acts=[2], weight=100)
class Augmenter(Event):
    """Augmenter - exclusive cards and relic."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.augmenter.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.augmenter.test_jax'),
                actions=[AddCardAction(card=JAX())]
            ),
            Option(
                name=LocalStr('events.augmenter.transform'),
                actions=[
                    ChooseTransformCardAction(),
                    ChooseTransformCardAction()
                ]
            ),
            Option(
                name=LocalStr('events.augmenter.mutagens'),
                actions=[AddRelicAction(relic=MutagenicStrength())]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.augmenter.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
