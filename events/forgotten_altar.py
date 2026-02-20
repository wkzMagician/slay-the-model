"""Event: Forgotten Altar - Act 2 Event

Trade Golden Idol for Bloody Idol, or sacrifice Max HP.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddCardAction
from actions.reward import AddRelicAction, LoseRelicAction
from actions.combat import ModifyMaxHpAction as ModifyMaxHPAction, LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Decay
from relics.global_relics.event import GoldenIdol, BloodyIdol


@register_event(event_id='forgotten_altar', floors='mid', weight=100)
class ForgottenAltar(Event):
    """Forgotten Altar - Golden Idol trade or Max HP sacrifice."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Ascension 15+."""
        return game_state.ascension >= 15
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.forgotten_altar.description'
        ))
        
        # Check if player has Golden Idol
        has_golden_idol = any(
            isinstance(r, GoldenIdol) for r in game_state.player.relics
        )
        
        # HP sacrifice percentage
        hp_percent = 0.35 if game_state.ascension >= 15 else 0.25
        
        # Build options
        options = []
        
        if has_golden_idol:
            options.append(Option(
                name=LocalStr('events.forgotten_altar.offer_golden_idol'),
                actions=[
                    LoseRelicAction(relic_type=GoldenIdol),
                    AddRelicAction(relic=BloodyIdol())
                ]
            ))
        
        options.extend([
            Option(
                name=LocalStr('events.forgotten_altar.sacrifice'),
                actions=[
                    ModifyMaxHPAction(amount=5),
                    LoseHPAction(percent=hp_percent)
                ]
            ),
            Option(
                name=LocalStr('events.forgotten_altar.desecrate'),
                actions=[AddCardAction(card=Decay())]
            ),
            Option(
                name=LocalStr('events.forgotten_altar.leave'),
                actions=[]
            )
        ])
        
        actions.append(SelectAction(
            title=LocalStr('events.forgotten_altar.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
