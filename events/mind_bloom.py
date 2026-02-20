"""Event: Mind Bloom - Act 3 Event

Powerful choices with consequences (boss fight, upgrade all, gold, or heal).
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddRandomCardAction, UpgradeCardAction, UpgradeAllCardsAction, AddCardAction
from actions.reward import AddGoldAction, AddRandomRelicAction, AddRelicAction
from actions.combat import HealAction, StartFightAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Normality, Doubt
from relics.global_relics.event import MarkOfBloom


@register_event(event_id='mind_bloom', floors='late', weight=100)
class MindBloom(Event):
    """Mind Bloom - powerful choices with consequences."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Ascension 15."""
        return game_state.ascension >= 15
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.mind_bloom.description'
        ))
        
        # Gold for "I am Rich" option (Floors 35-40)
        gold_amount = 25 if game_state.ascension >= 15 else 50
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.mind_bloom.i_am_war'),
                actions=[
                    StartFightAction(enemies=['random_act1_boss']),
                    AddRandomRelicAction(rarity='rare'),
                    AddGoldAction(amount=gold_amount),
                    AddRandomCardAction()
                ]
            ),
            Option(
                name=LocalStr('events.mind_bloom.i_am_awake'),
                actions=[
                    UpgradeAllCardsAction(),
                    AddRelicAction(relic=MarkOfBloom())
                ]
            ),
            Option(
                name=LocalStr('events.mind_bloom.i_am_rich'),
                actions=[
                    AddGoldAction(amount=999),
                    AddCardAction(card=Normality()),
                    AddCardAction(card=Normality())
                ],
                enabled=35 <= game_state.current_floor <= 40
            ),
            Option(
                name=LocalStr('events.mind_bloom.i_am_healthy'),
                actions=[
                    HealAction(percent=1.0),
                    AddCardAction(card=Doubt())
                ],
                enabled=game_state.current_floor >= 41
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.mind_bloom.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
