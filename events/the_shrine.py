"""
Event 4 - The Shrine
"""
from utils.result_types import BaseResult
from events.base_event import Event
from actions.card import AddRandomCardAction
from actions.display import SelectAction, DisplayTextAction
from actions.health import HealAction, LoseHPAction
from actions.reward import AddGoldAction
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option

@register_event(
    event_id="the_shrine",
    floors='early',
    weight=100
)
class ShrineEvent(Event):
    """Visit shrine and make a sacrifice"""
    
    def trigger(self) -> 'BaseResult':
        """Trigger shrine event"""
        from utils.result_types import NoneResult
        # Display event description
        from engine.game_state import game_state
        from actions.display import DisplayTextAction
        game_state.action_queue.add_action(DisplayTextAction(
            text_key="events.the_shrine.description"
        ))

        # Build options
        options = []

        # Option 1: Sacrifice HP for max energy
        options.append(Option(
            name=LocalStr("events.the_shrine.option1"),
            actions=[
                LoseHPAction(amount=10),
                AddRandomCardAction(pile="hand")
            ]
        ))

        # Option 2: Gain 100 gold
        options.append(Option(
            name=LocalStr("events.the_shrine.option2"),
            actions=[
                AddGoldAction(amount=100)
            ]
        ))

        # Option 3: Heal fully
        options.append(Option(
            name=LocalStr("events.the_shrine.option3"),
            actions=[
                HealAction(amount=999)
            ]
        ))

        # Display options and wait for selection
        game_state.action_queue.add_action(SelectAction(
            title=LocalStr("events.the_shrine.title"),
            options=options
        ))

        # End event after selection
        self.end_event()

        return NoneResult()
