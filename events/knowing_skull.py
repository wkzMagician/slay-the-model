"""Event: Knowing Skull - Act 2 Shrine Event

Repeatable HP for potion/gold/card trade.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.reward import AddRandomPotionAction, AddGoldAction
# TODO: Add LoseHPAction to actions.combat
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='knowing_skull', floors='mid', weight=100)
class KnowingSkull(Event):
    """Knowing Skull - repeatable HP for rewards."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if player has 13+ HP."""
        return game_state.player.current_hp >= 13
    
    def __init__(self):
        super().__init__()
        self.use_count = 0
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.knowing_skull.description'
        ))
        
        # HP cost: 10% Max HP, minimum 6, +1 per use
        base_hp = max(int(game_state.player.max_hp * 0.10), 6)
        hp_cost = base_hp + self.use_count
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.knowing_skull.potion'),
                actions=[
                    LoseHPAction(amount=hp_cost),
                    AddRandomPotionAction(character=game_state.player.character)
                ]
            ),
            Option(
                name=LocalStr('events.knowing_skull.riches'),
                actions=[
                    LoseHPAction(amount=hp_cost),
                    AddGoldAction(amount=90)
                ]
            ),
            Option(
                name=LocalStr('events.knowing_skull.success'),
                actions=[
                    LoseHPAction(amount=hp_cost),
                    AddRandomColorlessCardAction(rarity='uncommon')
                ]
            ),
            Option(
                name=LocalStr('events.knowing_skull.leave'),
                actions=[
                    LoseHPAction(amount=hp_cost)
                ]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.knowing_skull.title'),
            options=options
        ))
        
        self.use_count += 1
        self.end_event()
        return MultipleActionsResult(actions)
