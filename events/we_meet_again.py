"""Event: We Meet Again! - Shrine Event (All Acts)

Trade a potion, gold, or card for a random relic.
"""

import random
from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction
from actions.reward import AddRandomRelicAction, LoseGoldAction, LosePotionAction
from utils.types import RarityType
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='we_meet_again', acts='shared', weight=100)
class WeMeetAgain(Event):
    """We Meet Again! - trade items for relic."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.we_meet_again.description'
        ))
        
        # Build options based on available resources
        options = []
        
        # Option 1: Give Potion (if has potion)
        if game_state.player.potions:
            options.append(Option(
                name=LocalStr('events.we_meet_again.give_potion'),
                actions=[
                    LosePotionAction(index=0),  # Remove first potion
                    AddRandomRelicAction()
                ]
            ))
        
        # Option 2: Give Gold (50 to min(player.gold, 150) gold)
        if game_state.player.gold >= 50:
            gold_amount = random.randint(50, min(game_state.player.gold, 150))
            options.append(Option(
                name=LocalStr('events.we_meet_again.give_gold'),
                actions=[
                    LoseGoldAction(amount=gold_amount),
                    AddRandomRelicAction()
                ]
            ))
        
        # Option 3: Give Card (non-Basic, non-Curse, non-Bottled)
        options.append(Option(
            name=LocalStr('events.we_meet_again.give_card'),
            actions=[
                ChooseRemoveCardAction(
                    pile='deck',
                    exclude_rarities=[RarityType.STARTER, RarityType.CURSE]
                ),
                AddRandomRelicAction()
            ]
        ))
        
        # Option 4: Attack (he runs away)
        options.append(Option(
            name=LocalStr('events.we_meet_again.attack'),
            actions=[]  # Nothing happens
        ))
        
        actions.append(SelectAction(
            title=LocalStr('events.we_meet_again.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
