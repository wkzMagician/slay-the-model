"""
Event 5 - The Woman in Blue
"""
from events.base_event import Event
from actions.card import AddCardAction, RemoveCardAction
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddGoldAction
from actions.combat import DealDamageAction
from events.event_pool import register_event
from localization import LocalStr
from utils.types import RarityType

@register_event(
    event_id="woman_in_blue",
    floors='mid',
    weight=100
)
class WomanInBlueEvent(Event):
    """Meet the woman in blue and get a powerful blessing"""
    
    def trigger(self) -> str:
        """Trigger woman in blue encounter"""
        # Display event description
        from actions.display import DisplayTextAction
        self.action_queue.add_action(DisplayTextAction(
            text_key="events.woman_in_blue.description"
        ))
        
        # Build options
        options = []
        
        # Option 1: Heavy Blade (rare attack card)
        options.append(Option(
            name=LocalStr("events.woman_in_blue.option1"),
            actions=[
                AddCardAction(pile="hand"),
            ]
        ))
        
        # Option 2: Carnage (rare skill card)
        options.append(Option(
            name=LocalStr("events.woman_in_blue.option2"),
            actions=[
                AddCardAction(pile="hand"),
            ]
        ))
        
        # Option 3: 100 gold
        options.append(Option(
            name=LocalStr("events.woman_in_blue.option3"),
            actions=[
                AddGoldAction(amount=100),
            ]
        ))
        
        # Display options and wait for selection
        self.action_queue.add_action(SelectAction(
            title=LocalStr("events.woman_in_blue.title"),
            options=options
        ))
        
        return None
