"""Event: Mind Bloom - Act 3 Event

Powerful choices with consequences (boss fight, upgrade all, gold, or heal).
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import ChooseObtainCardAction, UpgradeAllCardsAction, AddCardAction
from actions.base import LambdaAction
from actions.reward import AddGoldAction, AddRandomRelicAction, AddRelicAction
from actions.combat import HealAction, StartFightAction
from utils.types import RarityType
from enemies.act1.the_guardian import TheGuardian
from enemies.act1.the_hexaghost import TheHexaghost
from enemies.act1.slime_boss import SlimeBoss
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Normality, Doubt
from relics.global_relics.event import MarkOfBloom


@register_event(category='event', event_id='mind_bloom', acts=[3], weight=100)
class MindBloom(Event):
    """Mind Bloom - powerful choices with consequences."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Appears on all ascensions in Act 3."""
        return True
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.mind_bloom.description'
        ))
        
        # Gold for "I am War" option (reduced on A13+)
        war_gold = 25 if game_state.ascension >= 13 else 50
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.mind_bloom.i_am_war'),
                detail=LocalStr('events.mind_bloom.war_detail', gold=war_gold),
                actions=[LambdaAction(self._start_war, args=[war_gold])],
            ),
            Option(
                name=LocalStr('events.mind_bloom.i_am_awake'),
                detail=LocalStr('events.mind_bloom.awake_detail'),
                actions=[
                    UpgradeAllCardsAction(),
                    AddRelicAction(relic=MarkOfBloom())
                ]
            ),
        ]
        if game_state.current_floor % 50 <= 40:
            options.append(Option(
                name=LocalStr('events.mind_bloom.i_am_rich'),
                detail=LocalStr('events.mind_bloom.rich_detail', gold=999),
                actions=[AddGoldAction(amount=999), AddCardAction(card=Normality()),
                         AddCardAction(card=Normality())],
            ))
        else:
            options.append(Option(
                name=LocalStr('events.mind_bloom.i_am_healthy'),
                detail=LocalStr('events.mind_bloom.healthy_detail'),
                actions=[HealAction(percent=1.0), AddCardAction(card=Doubt())],
            ))

        actions.append(InputRequestAction(
            title=LocalStr('events.mind_bloom.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)

    def _start_war(self, gold: int) -> None:
        """Generate a real Act 1 boss only when the fight option is selected."""
        boss_class = get_rng("misc").choice((TheGuardian, TheHexaghost, SlimeBoss))
        add_action(StartFightAction(
            enemies=[boss_class()],
            victory_actions=[
                AddRandomRelicAction(rarity=RarityType.RARE),
                AddGoldAction(amount=gold),
                ChooseObtainCardAction(
                    namespace=game_state.player.namespace, pile="deck", can_skip=True,
                    encounter_type="normal", use_rolling_offset=True, allow_upgraded=True,
                ),
            ],
        ), to_front=True)
