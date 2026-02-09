"""
Event 2 - The Cleric
"""
from utils.result_types import BaseResult
from events.base_event import Event
from actions.card import AddCardAction, ChooseRemoveCardAction, RemoveCardAction
from actions.display import SelectAction
from actions.reward import AddRelicAction, AddGoldAction
from actions.combat import HealAction
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option
from utils.types import RarityType

@register_event(
    event_id="the_cleric",
    floors='early',
    weight=100
)
class TheClericEvent(Event):
    """Meet the clerics and receive a random relic"""
    
    def trigger(self) -> 'BaseResult':
        """Trigger clerics encounter event"""
        from utils.result_types import MultipleActionsResult
        # Collect all actions
        actions = []

        # Display event description
        from actions.display import DisplayTextAction
        actions.append(DisplayTextAction(
            text_key="events.the_cleric.description"
        ))

        # Build options
        options = []

        # Option 1: Receive a random rare relic
        options.append(Option(
            name=LocalStr("events.the_cleric.option1"),
            actions=[
                AddRelicAction(relic="CeramicTorch"),
            ]
        ))

        # Option 2: Receive 200 gold
        options.append(Option(
            name=LocalStr("events.the_cleric.option2"),
            actions=[
                AddGoldAction(amount=200),
            ]
        ))

        # Option 3: Remove a card from deck
        options.append(Option(
            name=LocalStr("events.the_cleric.option3"),
            actions=[
                ChooseRemoveCardAction(pile="deck", amount=1),
            ]
        ))

        # Display options and wait for selection
        actions.append(SelectAction(
            title=LocalStr("events.the_cleric.title"),
            options=options
        ))

        return MultipleActionsResult(actions)
