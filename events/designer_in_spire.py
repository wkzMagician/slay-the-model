"""Event: Designer In-Spire - Act 2-3 Shrine Event

Gold for deck services (upgrade, remove, transform).
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction, ChooseUpgradeCardAction, ChooseTransformCardAction, UpgradeRandomCardAction
from actions.reward import LoseGoldAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='designer_in_spire', floors='mid', weight=100)
class DesignerInSpire(Event):
    """Designer In-Spire - gold for deck services."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if player has 75+ gold."""
        return game_state.player.gold >= 75
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.designer_in_spire.description'
        ))
        
        # Gold costs vary by A15+
        adjust_cost = 50 if game_state.ascension >= 15 else 40
        clean_cost = 75 if game_state.ascension >= 15 else 60
        full_cost = 110 if game_state.ascension >= 15 else 90
        punch_hp = 5 if game_state.ascension >= 15 else 3
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.designer_in_spire.adjustments'),
                actions=[
                    LoseGoldAction(amount=adjust_cost),
                    ChooseUpgradeCardAction()  # or 2 random upgrades
                ],
                enabled=game_state.player.gold >= adjust_cost
            ),
            Option(
                name=LocalStr('events.designer_in_spire.clean_up'),
                actions=[
                    LoseGoldAction(amount=clean_cost),
                    ChooseRemoveCardAction()  # or transform 2 cards
                ],
                enabled=game_state.player.gold >= clean_cost
            ),
            Option(
                name=LocalStr('events.designer_in_spire.full_service'),
                actions=[
                    LoseGoldAction(amount=full_cost),
                    ChooseRemoveCardAction(),
                    UpgradeRandomCardAction()
                ],
                enabled=game_state.player.gold >= full_cost
            ),
            Option(
                name=LocalStr('events.designer_in_spire.punch'),
                actions=[LoseHPAction(amount=punch_hp)]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.designer_in_spire.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
