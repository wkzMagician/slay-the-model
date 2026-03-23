"""Event: Wheel of Change - Shrine Event (All Acts)

Spin a wheel for random outcomes: gold, relic, heal, curse, remove card, or damage.
"""

import random
from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from actions.card import ChooseRemoveCardAction, AddCardAction
from actions.combat import HealAction, LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Decay


@register_event(event_id='wheel_of_change', acts='shared', weight=100)
class WheelOfChange(Event):
    """Wheel of Change - random outcome wheel."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.wheel_of_change.description'
        ))
        
        # Determine gold amount based on current act
        act_gold = {1: 100, 2: 200, 3: 300, 4: 300}
        gold_amount = act_gold.get(game_state.current_act, 100)
        
        # Note: AddRandomRelicAction doesn't support exclusions yet
        # Excluded relics: Bottled Flame, Bottled Lightning, Bottled Tornado, Whetstone
        excluded_relics = ['BottledFlame', 'BottledLightning', 'BottledTornado', 'Whetstone']
        
        # Determine outcomes
        outcomes = [
            AddGoldAction(amount=gold_amount),  # 100/200/300 gold based on Act 1/2/3
            AddRandomRelicAction(exclude_relics=excluded_relics),  # Exclude Bottled relics and Whetstone
            HealAction(percent=1.0),  # Full heal
            AddCardAction(card=Decay()),  # Gain Decay curse
            ChooseRemoveCardAction(),  # Remove a card
            # Take damage (10% or 15% on A15+)
            LoseHPAction(percent=0.15 if game_state.ascension >= 15 else 0.10)
        ]
        
        # Random outcome
        chosen_outcome = random.choice(outcomes)
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.wheel_of_change.play'),
                actions=[chosen_outcome]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.wheel_of_change.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
