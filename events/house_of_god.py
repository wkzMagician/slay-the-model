"""
Event 3 - The House of God
"""
from events.base_event import Event
from actions.card import AddCardAction
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddRelicAction, AddGoldAction
from actions.health import HealAction
from events.event_pool import register_event
from localization import LocalStr
from utils.types import RarityType

@register_event(
    event_id="house_of_god",
    floors='early',
    weight=100
)
class HouseOfGodEvent(Event):
    """Gain 1 of 3 powerful divine relics"""
    
    def trigger(self) -> str:
        """Trigger house of god event"""
        # Display event description
        from actions.display import DisplayTextAction
        self.action_queue.add_action(DisplayTextAction(
            text_key="events.house_of_god.description"
        ))
        
        # Build options
        options = []
        
        # Option 1: Burning Blood (rare)
        options.append(Option(
            name=LocalStr("events.house_of_god.option1"),
            actions=[
                AddRelicAction(relic="BurningBlood"),
                AddRandomRelicAction(rarities=[RarityType.RARE])
            ]
        ))
        
        # Option 2: Vajra (rare)
        options.append(Option(
            name=LocalStr("events.house_of_god.option2"),
            actions=[
                AddRelicAction(relic="Vajra")
            ]
        ))
        
        # Option 3: Empty Cage (rare)
        options.append(Option(
            name=LocalStr("events.house_of_god.option3"),
            actions=[
                AddRelicAction(relic="EmptyCage")
            ]
        ))
        
        # Display options and wait for selection
        self.action_queue.add_action(SelectAction(
            title=LocalStr("events.house_of_god.title"),
            options=options
        ))
        
        # End event after selection
        self.end_event()
        
        return None
