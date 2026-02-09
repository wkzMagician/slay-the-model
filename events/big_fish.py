"""
Event 1 - Big Fish
"""
from utils.result_types import BaseResult
from events.base_event import Event
from actions.card import AddRandomCardAction
from actions.display import SelectAction
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option
from utils.types import CardType, RarityType

@register_event(
    event_id="big_fish",
    floors='early',
    weight=100
)
class BigFishEvent(Event):
    """Gain 3 random common cards"""
    
    def trigger(self) -> 'BaseResult':
        """Trigger big fish blessing event"""
        from utils.result_types import MultipleActionsResult
        # Collect all actions
        actions = []

        # Display event description
        from actions.display import DisplayTextAction
        actions.append(DisplayTextAction(
            text_key="events.big_fish.description"
        ))

        # Build options
        options = []

        # Option 1: Receive 3 random common cards
        options.append(Option(
            name=LocalStr("events.big_fish.option1"),
            actions=[
                AddRandomCardAction(pile="hand", rarity=RarityType.COMMON),
                AddRandomCardAction(pile="hand", rarity=RarityType.COMMON),
                AddRandomCardAction(pile="hand", rarity=RarityType.COMMON),
            ]
        ))

        # Option 2: Receive 1 random uncommon card
        options.append(Option(
            name=LocalStr("events.big_fish.option2"),
            actions=[
                AddRandomCardAction(pile="hand", rarity=RarityType.UNCOMMON),
            ]
        ))

        # Option 3: Receive 3 random cards (mix of common and uncommon)
        for _ in range(3):
            options.append(Option(
                name=LocalStr("events.big_fish.option3", count=_+1),
                actions=[
                    AddRandomCardAction(pile="hand"),
                ]
            ))

        # Display options and wait for selection
        actions.append(SelectAction(
            title=LocalStr("events.big_fish.title"),
            options=options
        ))

        return MultipleActionsResult(actions)
