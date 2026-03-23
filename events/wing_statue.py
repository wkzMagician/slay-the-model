"""Event: Wing Statue - Act 1 Event

Remove a card for HP or gain gold with a high-damage attack.
"""

import random
from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction
from actions.reward import AddGoldAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='wing_statue', acts=[1], weight=100)
class WingStatue(Event):
    """Wing Statue - remove card for HP or gold for attack."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.wing_statue.description'
        ))
        
        # Gold: 50-80 random
        gold_amount = random.randint(50, 80)
        
        # Check if player has attack with 10+ base damage
        has_10_damage_attack = False
        for card in game_state.player.deck:
            if hasattr(card, 'card_type') and card.card_type == 'attack':
                if hasattr(card, 'base_damage') and card.base_damage >= 10:
                    has_10_damage_attack = True
                    break
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.wing_statue.pray'),
                actions=[
                    LoseHPAction(amount=7),
                    ChooseRemoveCardAction()
                ]
            )
        ]
        
        # Only show destroy option if player has qualifying attack
        if has_10_damage_attack:
            options.append(Option(
                name=LocalStr('events.wing_statue.destroy'),
                actions=[AddGoldAction(amount=gold_amount)]
            ))
        
        options.append(Option(
            name=LocalStr('events.wing_statue.leave'),
            actions=[]
        ))
        
        actions.append(InputRequestAction(
            title=LocalStr('events.wing_statue.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
