"""Event: Wing Statue - Act 1 Event

Remove a card for HP or gain gold with a high-damage attack.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction
from actions.reward import AddGoldAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from utils.types import CardType


@register_event(category='event', event_id='wing_statue', acts=[1], weight=100)
class WingStatue(Event):
    """Wing Statue - remove card for HP or gold for attack."""
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.wing_statue.description'
        ))
        
        # Gold: 50-80 random
        gold_amount = get_rng("misc").randint(50, 80)
        
        has_10_damage_attack = any(
            card.card_type == CardType.ATTACK and card.damage >= 10
            for card in game_state.player.deck
        )
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.wing_statue.pray'),
                detail=LocalStr('events.wing_statue.pray_detail', hp=7),
                actions=[
                    LoseHPAction(amount=7),
                    ChooseRemoveCardAction()
                ]
            )
        ]
        
        options.append(Option(
            name=LocalStr('events.wing_statue.destroy'),
            detail=LocalStr('events.gain_gold', gold=gold_amount),
            enabled=has_10_damage_attack,
            disabled_reason=LocalStr('events.wing_statue.require_attack', damage=10),
            actions=[AddGoldAction(amount=gold_amount)],
        ))

        options.append(Option(
            name=LocalStr('events.wing_statue.leave'),
            detail=LocalStr('events.no_effect'),
            actions=[]
        ))
        
        actions.append(InputRequestAction(
            title=LocalStr('events.wing_statue.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)
