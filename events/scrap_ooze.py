"""Event: Scrap Ooze - Act 1 Event

Reach into the ooze, lose HP, then roll for a relic. Ascension 15 raises the HP cost.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddRandomRelicAction
from actions.base import LambdaAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(category='event', event_id='scrap_ooze', acts=[1], weight=100)
class ScrapOoze(Event):
    """Scrap Ooze - HP for relic chance."""
    
    def __init__(self):
        super().__init__()
        self.attempt_count = 0
        self.relic_obtained = False

    def _hp_cost(self) -> int:
        base_hp = 5 if game_state.ascension >= 15 else 3
        return base_hp + self.attempt_count

    def _resolve_reach(self) -> None:
        relic_chance = 0.25 + (self.attempt_count * 0.10)
        if get_rng("misc").random() < relic_chance:
            self.relic_obtained = True
            add_actions([
                AddRandomRelicAction(),
                LambdaAction(self.end_event),
            ])
            return
        self.attempt_count += 1
        self.trigger()
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.scrap_ooze.description'
        ))
        
        options = []
        
        if not self.relic_obtained:
            options.append(Option(
                name=LocalStr('events.scrap_ooze.reach'),
                detail=LocalStr('events.scrap_ooze.reach_detail', hp=self._hp_cost(), chance=min(100, 25 + self.attempt_count * 10)),
                actions=[
                    LoseHPAction(amount=self._hp_cost()),
                    LambdaAction(self._resolve_reach),
                ]
            ))
        
        options.append(Option(
            name=LocalStr('events.scrap_ooze.leave'),
            detail=LocalStr('events.no_effect'),
            actions=[LambdaAction(self.end_event)]
        ))
        
        actions.append(InputRequestAction(
            title=LocalStr('events.scrap_ooze.title'),
            options=options
        ))
        
        add_actions(actions)
