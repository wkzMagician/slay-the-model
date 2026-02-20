"""Event: Bonfire Spirits - Shrine Event (All Acts)

Sacrifice a card to the spirits for rewards based on card rarity.
- Basic: Nothing
- Common: Heal 5 HP
- Uncommon: Full heal
- Rare: +10 Max HP + Full heal
- Curse: Receive Spirit Poop relic (TODO: implement relic)
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction
from actions.combat import HealAction, ModifyMaxHpAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='bonfire_spirits', floors='all', weight=100)
class BonfireSpirits(Event):
    """Bonfire Spirits - sacrifice card for reward by rarity."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.bonfire_spirits.description'
        ))
        
        # Build options
        # TODO: Implement proper card sacrifice with rarity-based rewards
        # For now, use ChooseRemoveCardAction with heal reward
        options = [
            Option(
                name=LocalStr('events.bonfire_spirits.offer'),
                actions=[
                    ChooseRemoveCardAction(),
                    HealAction(amount=5)  # Simplified reward
                ]
            ),
            Option(
                name=LocalStr('events.bonfire_spirits.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.bonfire_spirits.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
