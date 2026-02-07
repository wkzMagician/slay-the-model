"""
Event 5 - The Woman in Blue
"""
from utils.result_types import BaseResult
from events.base_event import Event
from actions.card import AddRandomCardAction, RemoveCardAction
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddGoldAction
from actions.combat import DealDamageAction
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option
from utils.types import RarityType

@register_event(
    event_id="woman_in_blue",
    floors='mid',
    weight=100
)
class WomanInBlueEvent(Event):
    """Meet the woman in blue and get a powerful blessing"""
    
    def trigger(self) -> 'BaseResult':
        """Trigger woman in blue encounter"""
        from utils.result_types import NoneResult
        # Display event description
        from engine.game_state import game_state
        from actions.display import DisplayTextAction
        game_state.action_queue.add_action(DisplayTextAction(
            text_key="events.woman_in_blue.description"
        ))

        # Build options
        options = []

        # Option 1: Heavy Blade (rare attack card)
        options.append(Option(
            name=LocalStr("events.woman_in_blue.option1"),
            actions=[
                AddRandomCardAction(pile="hand", rarity=RarityType.RARE),
            ]
        ))

        # Option 2: Carnage (rare skill card)
        options.append(Option(
            name=LocalStr("events.woman_in_blue.option2"),
            actions=[
                AddRandomCardAction(pile="hand", rarity=RarityType.RARE),
            ]
        ))

        # Option 3: 100 gold
        options.append(Option(
            name=LocalStr("events.woman_in_blue.option3"),
            actions=[
                AddGoldAction(amount=100),
            ]
        ))

        # Display options and wait for selection
        game_state.action_queue.add_action(SelectAction(
            title=LocalStr("events.woman_in_blue.title"),
            options=options
        ))

        return NoneResult()
