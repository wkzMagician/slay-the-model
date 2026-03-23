"""Event: Knowing Skull - Act 2 Shrine Event

Repeatable HP for potion/gold/card trade.
"""

from actions.base import LambdaAction
from actions.combat import LoseHPAction
from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddRandomCardAction
from utils.types import RarityType
from actions.reward import AddRandomPotionAction, AddGoldAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='knowing_skull', acts=[2], weight=100)
class KnowingSkull(Event):
    """
    Knowing Skull - repeatable HP for rewards.
    
    [Potion] Lose 6% (A15+: 8%) of Max HP (+1 per use). Obtain a random potion.
    [Riches] Lose 6% (A15+: 8%) of Max HP (+1 per use). Gain 90 Gold.
    [Success] Lose 6% (A15+: 8%) of Max HP (+1 per use). Obtain a random Uncommon Colorless card.
    [Leave] Nothing happens.
    """
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if player has 13+ HP."""
        return game_state.player.hp >= 13
    
    def __init__(self):
        super().__init__()
        self.use_count = 0
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description only on first entry
        if self.use_count == 0:
            actions.append(DisplayTextAction(
                text_key='events.knowing_skull.description'
            ))
        
        # HP cost: 6% (8% A15+) of Max HP, minimum 6, +1 per use
        hp_percent = 0.08 if game_state.ascension >= 15 else 0.06
        base_hp = max(int(game_state.player.max_hp * hp_percent), 6)
        hp_cost = base_hp + self.use_count
        
        # Build options - loop until player chooses Leave
        options = [
            Option(
                name=LocalStr('events.knowing_skull.potion'),
                actions=[
                    LoseHPAction(amount=hp_cost),
                    AddRandomPotionAction(character=game_state.player.character),
                    LambdaAction(lambda: self._increment_use())
                ]
            ),
            Option(
                name=LocalStr('events.knowing_skull.riches'),
                actions=[
                    LoseHPAction(amount=hp_cost),
                    AddGoldAction(amount=90),
                    LambdaAction(lambda: self._increment_use())
                ]
            ),
            Option(
                name=LocalStr('events.knowing_skull.success'),
                actions=[
                    LoseHPAction(amount=hp_cost),
                    AddRandomCardAction(namespace='colorless', rarity=RarityType.UNCOMMON),
                    LambdaAction(lambda: self._increment_use())
                ]
            ),
            Option(
                name=LocalStr('events.knowing_skull.leave'),
                actions=[]  # Leave costs nothing and ends the event
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.knowing_skull.title'),
            options=options
        ))
        
        # Don't end event here - it will be ended by the InputRequestAction result
        # Only end when player chooses Leave (which doesn't have end_event in its actions)
        return MultipleActionsResult(actions)
    
    def _increment_use(self):
        """Increment use count when a reward is chosen."""
        self.use_count += 1
