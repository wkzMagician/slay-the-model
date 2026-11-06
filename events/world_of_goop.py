"""Event: World of Goop - Act 1 Event

Forced gold loss or gain gold at HP cost.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddGoldAction, LoseGoldAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(category='event', event_id='world_of_goop', acts=[1], weight=100)
class WorldOfGoop(Event):
    """World of Goop - lose gold or gain gold for HP."""
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.world_of_goop.description'
        ))
        
        # Gold loss: 20-50 normal, 35-75 on A15+
        if game_state.ascension >= 15:
            gold_loss = min(get_rng("misc").randint(35, 75), game_state.player.gold)
        else:
            gold_loss = min(get_rng("misc").randint(20, 50), game_state.player.gold)
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.world_of_goop.gather'),
                detail=LocalStr('events.world_of_goop.gather_detail'),
                actions=[
                    LoseHPAction(amount=11),
                    AddGoldAction(amount=75)
                ]
            ),
            Option(
                name=LocalStr('events.world_of_goop.leave'),
                detail=LocalStr('events.world_of_goop.leave_detail', gold=gold_loss),
                actions=[LoseGoldAction(amount=gold_loss)]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.world_of_goop.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)
